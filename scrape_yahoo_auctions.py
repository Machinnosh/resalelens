"""
Yahoo Auctions Japan (ヤフオク) completed/sold items scraper.
Uses httpx + BeautifulSoup to scrape sold luxury brand items.
"""

import httpx
from bs4 import BeautifulSoup
import json
import time
import random
import urllib.parse
import os
import re
from datetime import datetime

BASE_URL = "https://auctions.yahoo.co.jp/search/search"
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

QUERIES = [
    "エルメス バーキン",
    "シャネル マトラッセ",
    "ルイヴィトン ネヴァーフル",
    "ロレックス サブマリーナ",
    "ロレックス デイトナ",
    "オメガ スピードマスター",
    "カルティエ タンク",
    "グッチ マーモント",
    "プラダ ガレリア",
    "コーチ タビー",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "ja,en-US;q=0.7,en;q=0.3",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

# Multiple selector strategies since Yahoo changes HTML frequently
SELECTOR_STRATEGIES = [
    # Strategy 1: Modern layout with Product class
    {
        "name": "Product class",
        "container": ".Product",
        "title": ".Product__titleLink, .Product__title a, .Product__title",
        "price": ".Product__priceValue, .Product__price",
        "link": ".Product__titleLink, .Product__title a",
    },
    # Strategy 2: Search result list items
    {
        "name": "SearchResult",
        "container": ".SearchResult, .SearchResultItem",
        "title": ".SearchResult__titleLink, .SearchResultItem__titleLink, a[data-auction-title]",
        "price": ".SearchResult__priceValue, .SearchResultItem__price",
        "link": ".SearchResult__titleLink, .SearchResultItem__titleLink, a[data-auction-title]",
    },
    # Strategy 3: Older table-based layout
    {
        "name": "table-based",
        "container": "tr.Result, .cf table tbody tr",
        "title": "a.a1, h3 a, .title a",
        "price": ".ePrice, .decPrice, .price",
        "link": "a.a1, h3 a, .title a",
    },
    # Strategy 4: Generic list items with auction links
    {
        "name": "list-item generic",
        "container": "li[class*='Product'], li[class*='auction'], div[class*='Product'], div[class*='result']",
        "title": "a[href*='auctions.yahoo.co.jp/jp/auction/'], a[href*='page.auctions.yahoo.co.jp/']",
        "price": "[class*='price'], [class*='Price']",
        "link": "a[href*='auctions.yahoo.co.jp/jp/auction/'], a[href*='page.auctions.yahoo.co.jp/']",
    },
    # Strategy 5: Broadest possible - just find all auction links
    {
        "name": "broad auction links",
        "container": None,  # special: scan all links
        "title": None,
        "price": None,
        "link": None,
    },
]


def extract_price(text: str) -> int | None:
    """Extract numeric price from text like '1,234,567円'."""
    if not text:
        return None
    nums = re.findall(r"[\d,]+", text.replace(",", "").replace("，", ""))
    # re-extract with commas kept for original
    nums = re.findall(r"[\d]+", text.replace(",", "").replace("，", ""))
    if nums:
        try:
            return int(nums[0])
        except ValueError:
            return None
    return None


def try_broad_extraction(soup: BeautifulSoup) -> list[dict]:
    """Broadest strategy: find all auction item links and nearby price info."""
    items = []
    seen_urls = set()

    # Find all links pointing to auction item pages
    auction_links = soup.find_all("a", href=re.compile(
        r"(auctions\.yahoo\.co\.jp/jp/auction/|page\.auctions\.yahoo\.co\.jp/jp/auction/)"
    ))

    for link in auction_links:
        url = link.get("href", "")
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)

        title = link.get_text(strip=True)
        if not title or len(title) < 3:
            # Try to get title from nearby elements
            title = link.get("title", "") or link.get("data-auction-title", "")
        if not title or len(title) < 3:
            continue

        # Look for price in parent/sibling elements
        price_text = None
        parent = link.parent
        for _ in range(5):  # walk up to 5 levels
            if parent is None:
                break
            price_el = parent.find(string=re.compile(r"[\d,]+円"))
            if price_el:
                price_text = price_el.strip()
                break
            price_el = parent.find(class_=re.compile(r"[Pp]rice"))
            if price_el:
                price_text = price_el.get_text(strip=True)
                break
            parent = parent.parent

        price = extract_price(price_text) if price_text else None

        items.append({
            "title": title,
            "price": price,
            "price_text": price_text,
            "url": url,
        })

    return items


def parse_with_strategy(soup: BeautifulSoup, strategy: dict) -> list[dict]:
    """Try to extract items using a specific CSS selector strategy."""
    if strategy["container"] is None:
        return try_broad_extraction(soup)

    containers = soup.select(strategy["container"])
    if not containers:
        return []

    items = []
    for container in containers:
        # Title
        title_el = container.select_one(strategy["title"]) if strategy["title"] else None
        title = title_el.get_text(strip=True) if title_el else None

        # Price
        price_el = container.select_one(strategy["price"]) if strategy["price"] else None
        price_text = price_el.get_text(strip=True) if price_el else None
        price = extract_price(price_text) if price_text else None

        # URL
        link_el = container.select_one(strategy["link"]) if strategy["link"] else None
        url = link_el.get("href", "") if link_el else ""

        if title and len(title) >= 3:
            items.append({
                "title": title,
                "price": price,
                "price_text": price_text,
                "url": url,
            })

    return items


def scrape_query(client: httpx.Client, query: str) -> list[dict]:
    """Scrape sold items for a given query."""
    params = {
        "p": query,
        "select": "sold",
        "n": "50",
    }
    url = f"{BASE_URL}?{urllib.parse.urlencode(params)}"
    print(f"  Fetching: {url}")

    try:
        resp = client.get(url, follow_redirects=True, timeout=30.0)
        resp.raise_for_status()
    except httpx.HTTPStatusError as e:
        print(f"  HTTP error {e.response.status_code} for query '{query}'")
        return []
    except httpx.RequestError as e:
        print(f"  Request error for query '{query}': {e}")
        return []

    print(f"  Response: {resp.status_code}, length={len(resp.text)} chars, url={resp.url}")

    soup = BeautifulSoup(resp.text, "html.parser")

    # Debug: save raw HTML for first query to inspect
    debug_path = os.path.join(DATA_DIR, f"debug_{urllib.parse.quote(query, safe='')[:30]}.html")
    with open(debug_path, "w", encoding="utf-8") as f:
        f.write(resp.text)
    print(f"  Saved debug HTML to {debug_path}")

    # Try each selector strategy
    for strategy in SELECTOR_STRATEGIES:
        items = parse_with_strategy(soup, strategy)
        if items:
            print(f"  Strategy '{strategy['name']}' found {len(items)} items")
            return items
        else:
            print(f"  Strategy '{strategy['name']}' found 0 items")

    # If nothing worked, report what we see
    print(f"  WARNING: No items found for '{query}'.")
    # Print some page structure hints
    all_classes = set()
    for tag in soup.find_all(True, class_=True):
        for c in tag.get("class", []):
            if any(kw in c.lower() for kw in ["product", "item", "result", "auction", "list", "price"]):
                all_classes.add(c)
    if all_classes:
        print(f"  Potentially relevant CSS classes found: {sorted(all_classes)[:20]}")

    return []


def main():
    print(f"=== Yahoo Auctions Japan Scraper ===")
    print(f"Started at: {datetime.now().isoformat()}")
    print(f"Queries: {len(QUERIES)}\n")

    all_results = {}
    total_items = 0

    with httpx.Client(headers=HEADERS, http2=False) as client:
        for i, query in enumerate(QUERIES, 1):
            print(f"[{i}/{len(QUERIES)}] Scraping: {query}")
            items = scrape_query(client, query)
            all_results[query] = items
            total_items += len(items)
            print(f"  => Found {len(items)} items\n")

            if i < len(QUERIES):
                delay = random.uniform(2.0, 3.0)
                print(f"  Waiting {delay:.1f}s...")
                time.sleep(delay)

    # Summary
    print("=" * 50)
    print("SUMMARY:")
    for query, items in all_results.items():
        print(f"  {query}: {len(items)} items")
    print(f"  TOTAL: {total_items} items")

    # Save to JSON
    output_path = os.path.join(DATA_DIR, "yahoo_auction_results.json")
    output = {
        "scraped_at": datetime.now().isoformat(),
        "total_items": total_items,
        "queries": {},
    }
    for query, items in all_results.items():
        output["queries"][query] = {
            "count": len(items),
            "items": items,
        }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\nResults saved to: {output_path}")
    print(f"Finished at: {datetime.now().isoformat()}")


if __name__ == "__main__":
    main()
