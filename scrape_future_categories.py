"""
ResaleLens - Future Category Scraper (Phase 2-4)
Scrapes sold/completed items from Yahoo Auctions and car listing sites
for categories planned beyond the MVP luxury brand focus.
"""

import httpx
import json
import time
import random
import os
import sys
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import quote

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ja,en-US;q=0.7,en;q=0.3",
}

DELAY_RANGE = (2, 3)  # seconds between requests

# ---------------------------------------------------------------------------
# Category definitions
# ---------------------------------------------------------------------------
CATEGORIES = {
    "apple": {
        "phase": 2,
        "label": "Apple Products",
        "output": "future_apple_results.json",
        "queries": [
            "iPhone 15 Pro",
            "iPhone 14",
            "MacBook Pro M3",
            "iPad Pro M2",
            "Apple Watch Ultra",
        ],
        "sources": ["yahoo_auctions"],
    },
    "gaming": {
        "phase": 3,
        "label": "Gaming",
        "output": "future_gaming_results.json",
        "queries": [
            "Nintendo Switch",
            "PlayStation 5",
            "Steam Deck",
        ],
        "sources": ["yahoo_auctions"],
    },
    "sneakers": {
        "phase": 3,
        "label": "Sneakers",
        "output": "future_sneakers_results.json",
        "queries": [
            "Nike Air Jordan 1",
            "Nike Dunk Low",
            "adidas Yeezy",
        ],
        "sources": ["yahoo_auctions"],
    },
    "cars": {
        "phase": 4,
        "label": "Cars",
        "output": "future_cars_results.json",
        "queries": [
            "トヨタ アルファード",
            "レクサス RX",
            "メルセデス Cクラス",
        ],
        "sources": ["yahoo_auctions", "carsensor"],
    },
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def polite_delay():
    """Sleep a random amount between requests to be polite."""
    d = random.uniform(*DELAY_RANGE)
    time.sleep(d)


def clean_price(text: str) -> int | None:
    """Extract integer yen price from text like '12,345円'."""
    if not text:
        return None
    import re
    text = text.replace(",", "").replace("，", "").replace(" ", "").replace("\u3000", "")
    m = re.search(r"(\d+)", text)
    return int(m.group(1)) if m else None


# ---------------------------------------------------------------------------
# Yahoo Auctions scraper (sold items)
# ---------------------------------------------------------------------------

def scrape_yahoo_auctions(query: str, client: httpx.Client) -> list[dict]:
    """Scrape sold/completed listings from Yahoo Auctions search."""
    url = (
        "https://auctions.yahoo.co.jp/search/search"
        f"?p={quote(query)}&select=sold&n=50"
    )
    items = []
    print(f"  [Yahoo] Fetching: {query} ...")

    try:
        resp = client.get(url, timeout=20, follow_redirects=True)
        resp.raise_for_status()
    except httpx.HTTPStatusError as e:
        print(f"    HTTP error {e.response.status_code} for Yahoo query '{query}'")
        return items
    except httpx.RequestError as e:
        print(f"    Request error for Yahoo query '{query}': {e}")
        return items

    soup = BeautifulSoup(resp.text, "html.parser")

    # Yahoo Auctions search results use several possible structures.
    # We try multiple selectors to be resilient to layout changes.

    # Strategy 1: product list items with data attributes
    product_cards = soup.select("li.Product")
    if not product_cards:
        # Strategy 2: older layout
        product_cards = soup.select("div.Result__body li")
    if not product_cards:
        # Strategy 3: table rows (very old layout)
        product_cards = soup.select("table.list tr")
    if not product_cards:
        # Strategy 4: generic anchor-based fallback
        product_cards = soup.select("ul.Products__items li")

    for card in product_cards:
        try:
            # Try to find title
            title_el = (
                card.select_one("a.Product__titleLink")
                or card.select_one("h3 a")
                or card.select_one("a[href*='page.auctions.yahoo.co.jp']")
                or card.select_one("a[href*='auctions.yahoo.co.jp/jp/auction']")
            )
            if not title_el:
                continue

            title = title_el.get_text(strip=True)
            link = title_el.get("href", "")

            # Price – look for the sold price element
            price_el = (
                card.select_one(".Product__priceValue")
                or card.select_one(".Product__price")
                or card.select_one("span.price")
                or card.select_one(".dec")
            )
            price_text = price_el.get_text(strip=True) if price_el else ""
            price = clean_price(price_text)

            items.append({
                "title": title,
                "price": price,
                "price_text": price_text,
                "url": link,
                "source": "yahoo_auctions",
                "query": query,
            })
        except Exception as exc:
            # Skip individual card parse errors
            continue

    # Fallback: if structured selectors found nothing, try grabbing any
    # auction links on the page.
    if not items:
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            if "page.auctions.yahoo.co.jp" in href or "/jp/auction/" in href:
                title = a_tag.get_text(strip=True)
                if not title or len(title) < 5:
                    continue
                # Try to find a nearby price
                parent = a_tag.parent
                price_text = ""
                if parent:
                    for span in parent.find_all(["span", "div"]):
                        txt = span.get_text(strip=True)
                        if "円" in txt or txt.replace(",", "").isdigit():
                            price_text = txt
                            break
                price = clean_price(price_text)
                items.append({
                    "title": title,
                    "price": price,
                    "price_text": price_text,
                    "url": href,
                    "source": "yahoo_auctions",
                    "query": query,
                })
        # Deduplicate by URL
        seen = set()
        deduped = []
        for it in items:
            if it["url"] not in seen:
                seen.add(it["url"])
                deduped.append(it)
        items = deduped

    print(f"    -> {len(items)} items found")
    return items


# ---------------------------------------------------------------------------
# Carsensor scraper (used car listings)
# ---------------------------------------------------------------------------

def scrape_carsensor(query: str, client: httpx.Client) -> list[dict]:
    """Scrape car listings from carsensor.net free-text search."""
    url = (
        "https://www.carsensor.net/usedcar/search.php"
        f"?STID=CS210610&CAESSION=101_1&CAESSION=101_2&CESSION=0"
        f"&FREEWORD={quote(query)}"
    )
    items = []
    print(f"  [Carsensor] Fetching: {query} ...")

    try:
        resp = client.get(url, timeout=20, follow_redirects=True)
        resp.raise_for_status()
    except httpx.HTTPStatusError as e:
        print(f"    HTTP error {e.response.status_code} for Carsensor query '{query}'")
        return items
    except httpx.RequestError as e:
        print(f"    Request error for Carsensor query '{query}': {e}")
        return items

    soup = BeautifulSoup(resp.text, "html.parser")

    # Carsensor lists cars in <div class="casetListItem"> or similar wrappers
    car_cards = soup.select("div.cassetteWrap")
    if not car_cards:
        car_cards = soup.select("div.casetListItem")
    if not car_cards:
        car_cards = soup.select("section.cassette")
    if not car_cards:
        # Broad fallback: look for list items with car links
        car_cards = soup.select("div[class*='cassette']")

    for card in car_cards:
        try:
            title_el = (
                card.select_one("a.cassetteMain__titleLink")
                or card.select_one("h3 a")
                or card.select_one("a[class*='title']")
                or card.select_one("p.cassetteMain__title a")
            )
            if not title_el:
                # Try any link
                title_el = card.select_one("a[href*='/usedcar/detail/']")
            if not title_el:
                continue

            title = title_el.get_text(strip=True)
            link = title_el.get("href", "")
            if link and not link.startswith("http"):
                link = "https://www.carsensor.net" + link

            price_el = (
                card.select_one("span.cassetteMain__priceValue")
                or card.select_one("span[class*='price']")
                or card.select_one("p.cassetteMain__price")
            )
            price_text = price_el.get_text(strip=True) if price_el else ""
            price = clean_price(price_text)
            # Carsensor often shows prices in 万円 (ten-thousands of yen)
            if price and price_text and "万" in price_text:
                price = price * 10000

            items.append({
                "title": title,
                "price": price,
                "price_text": price_text,
                "url": link,
                "source": "carsensor",
                "query": query,
            })
        except Exception:
            continue

    # Fallback link scan
    if not items:
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            if "/usedcar/detail/" in href:
                title = a_tag.get_text(strip=True)
                if not title or len(title) < 3:
                    continue
                full_url = href if href.startswith("http") else "https://www.carsensor.net" + href
                items.append({
                    "title": title,
                    "price": None,
                    "price_text": "",
                    "url": full_url,
                    "source": "carsensor",
                    "query": query,
                })
        # Deduplicate
        seen = set()
        deduped = []
        for it in items:
            if it["url"] not in seen:
                seen.add(it["url"])
                deduped.append(it)
        items = deduped

    print(f"    -> {len(items)} items found")
    return items


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------

def run():
    print("=" * 60)
    print("ResaleLens - Future Category Scraper (Phase 2-4)")
    print(f"Run at: {datetime.now().isoformat()}")
    print("=" * 60)

    summary = {}

    with httpx.Client(headers=HEADERS, http2=False) as client:
        for cat_key, cat in CATEGORIES.items():
            phase = cat["phase"]
            label = cat["label"]
            print(f"\n--- Phase {phase}: {label} ---")

            all_items = []

            for query in cat["queries"]:
                if "yahoo_auctions" in cat["sources"]:
                    items = scrape_yahoo_auctions(query, client)
                    all_items.extend(items)
                    polite_delay()

                if "carsensor" in cat["sources"]:
                    items = scrape_carsensor(query, client)
                    all_items.extend(items)
                    polite_delay()

            # Save results
            out_path = os.path.join(DATA_DIR, cat["output"])
            output = {
                "category": label,
                "phase": phase,
                "scraped_at": datetime.now().isoformat(),
                "total_items": len(all_items),
                "items": all_items,
            }
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(output, f, ensure_ascii=False, indent=2)

            summary[label] = len(all_items)
            print(f"  Saved {len(all_items)} items -> {out_path}")

    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    total = 0
    for label, count in summary.items():
        print(f"  {label:25s} : {count:4d} items")
        total += count
    print(f"  {'TOTAL':25s} : {total:4d} items")
    print("=" * 60)


if __name__ == "__main__":
    run()
