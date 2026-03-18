"""
Mercari Japan scraper for ResaleLens.

Strategy:
- Mercari's search API (api.mercari.jp) requires authentication (401 without token).
- Mercari's SPA renders search results client-side, so regular HTML scraping gets no items.
- Using Googlebot User-Agent triggers SSR with __NEXT_DATA__ containing item data via
  the /v2/entities:search endpoint baked into swrData.
- The SSR endpoint ignores the sold_out status filter and returns on-sale listings.
  These are still valuable for market price analysis.
- We extract items from __NEXT_DATA__ -> props.pageProps.swrData -> (key containing "entities:search") -> items.

Queries: 6 luxury brand item searches.
Output: data/mercari_results.json
"""

import json
import os
import random
import re
import sys
import time
from pathlib import Path
from urllib.parse import quote

# Force UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import httpx
from bs4 import BeautifulSoup

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
OUTPUT_FILE = DATA_DIR / "mercari_results.json"

QUERIES = [
    "エルメス バーキン",
    "シャネル フラップ",
    "ルイヴィトン ネヴァーフル",
    "ロレックス サブマリーナ",
    "ロレックス デイトナ",
    "オメガ スピードマスター",
]

# Googlebot UA triggers server-side rendering with actual item data
HEADERS_BOT = {
    "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Accept-Language": "ja-JP,ja;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# Condition ID mapping from Mercari
CONDITION_MAP = {
    "1": "新品、未使用",
    "2": "未使用に近い",
    "3": "目立った傷や汚れなし",
    "4": "やや傷や汚れあり",
    "5": "傷や汚れあり",
    "6": "全体的に状態が悪い",
}


def delay():
    """Random delay between requests."""
    wait = random.uniform(3, 5)
    print(f"  (waiting {wait:.1f}s)")
    time.sleep(wait)


def extract_items_from_next_data(html: str) -> list[dict]:
    """Parse __NEXT_DATA__ and extract items from swrData."""
    soup = BeautifulSoup(html, "html.parser")
    script = soup.find("script", id="__NEXT_DATA__")
    if not script or not script.string:
        return []

    nd = json.loads(script.string)
    swr = nd.get("props", {}).get("pageProps", {}).get("swrData", {})

    for key, val in swr.items():
        if not isinstance(val, dict):
            continue
        if "items" not in val:
            continue
        # The entities:search key contains the main search results
        if "entities:search" in key or "search" in key.lower():
            raw_items = val["items"]
            if raw_items:
                return raw_items

    # Fallback: find any key with an items array
    for key, val in swr.items():
        if isinstance(val, dict) and "items" in val and isinstance(val["items"], list) and len(val["items"]) > 0:
            return val["items"]

    return []


def parse_items(raw_items: list[dict]) -> list[dict]:
    """Convert raw Mercari item dicts to our standard format."""
    results = []
    for it in raw_items:
        if not isinstance(it, dict):
            continue
        item_id = it.get("id", "")
        name = it.get("name", "")
        price_raw = it.get("price", 0)
        price = int(price_raw) if str(price_raw).isdigit() else 0

        # Timestamps are Unix epoch seconds
        created_ts = it.get("created", "")
        updated_ts = it.get("updated", "")
        created_str = ""
        updated_str = ""
        try:
            if created_ts and str(created_ts).isdigit():
                created_str = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(int(created_ts)))
        except (ValueError, OSError):
            pass
        try:
            if updated_ts and str(updated_ts).isdigit():
                updated_str = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(int(updated_ts)))
        except (ValueError, OSError):
            pass

        condition_id = str(it.get("itemConditionId", ""))
        condition = CONDITION_MAP.get(condition_id, condition_id)

        status = it.get("status", "")
        thumbnail = ""
        thumbs = it.get("thumbnails", [])
        if isinstance(thumbs, list) and thumbs:
            thumbnail = thumbs[0]

        brand_info = it.get("itemBrand", {})
        brand_name = brand_info.get("name", "") if isinstance(brand_info, dict) else ""

        results.append({
            "title": name,
            "price": price,
            "status": status,
            "listed_date": created_str,
            "updated_date": updated_str,
            "sold_date": updated_str if "SOLD" in status else "",
            "url": f"https://jp.mercari.com/item/{item_id}",
            "condition": condition,
            "brand": brand_name,
            "image": thumbnail,
            "item_id": item_id,
        })
    return results


def scrape_query(client: httpx.Client, query: str) -> tuple[list[dict], str]:
    """
    Scrape Mercari for a single query.
    Returns (items, approach_used).
    """
    url = f"https://jp.mercari.com/search?keyword={quote(query)}&sort=created_time&order=desc"

    # Approach 1: Try Mercari search API (requires auth - likely fails)
    print("  Approach 1: Mercari search API...")
    api_url = "https://api.mercari.jp/search_index/search"
    api_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Platform": "web",
        "Referer": "https://jp.mercari.com/",
        "Origin": "https://jp.mercari.com",
    }
    payload = {
        "keyword": query,
        "status": ["STATUS_SOLD_OUT"],
        "sort": "SORT_CREATED_TIME",
        "order": "ORDER_DESC",
        "limit": 30,
    }
    try:
        resp = client.post(api_url, json=payload, headers=api_headers, timeout=15)
        print(f"    status={resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            raw = data.get("items", [])
            if raw:
                return parse_items(raw), "api"
    except Exception as e:
        print(f"    error: {e}")

    delay()

    # Approach 2: Googlebot SSR with __NEXT_DATA__ extraction (with retry on 429)
    for attempt in range(3):
        print(f"  Approach 2: Googlebot SSR (__NEXT_DATA__)... (attempt {attempt+1})")
        try:
            resp = client.get(url, headers=HEADERS_BOT, timeout=20)
            print(f"    status={resp.status_code}, length={len(resp.text)}")
            if resp.status_code == 200:
                raw_items = extract_items_from_next_data(resp.text)
                if raw_items:
                    items = parse_items(raw_items)
                    return items, "ssr_next_data"
                break  # 200 but no items - don't retry
            elif resp.status_code == 429:
                wait = random.uniform(10, 20)
                print(f"    Rate limited. Waiting {wait:.0f}s before retry...")
                time.sleep(wait)
                continue
            else:
                break  # Other error - don't retry
        except Exception as e:
            print(f"    error: {e}")
            break

    delay()

    # Approach 3: Standard UA HTML parsing (SPA - probably empty)
    print("  Approach 3: Standard HTML parsing...")
    std_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept-Language": "ja-JP,ja;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    try:
        resp = client.get(url, headers=std_headers, timeout=20)
        print(f"    status={resp.status_code}, length={len(resp.text)}")
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            # Try to find item links
            links = soup.find_all("a", href=re.compile(r"/item/m\d+"))
            if links:
                items = []
                for a in links[:30]:
                    href = a["href"]
                    item_url = href if href.startswith("http") else f"https://jp.mercari.com{href}"
                    items.append({
                        "title": a.get_text(strip=True) or "",
                        "price": 0,
                        "status": "",
                        "listed_date": "",
                        "updated_date": "",
                        "sold_date": "",
                        "url": item_url,
                        "condition": "",
                        "brand": "",
                        "image": "",
                        "item_id": "",
                    })
                if items:
                    return items, "html_links"
    except Exception as e:
        print(f"    error: {e}")

    return [], "failed"


def main():
    all_results = {}
    total_count = 0
    approach_summary = {}

    with httpx.Client(http2=False, follow_redirects=True) as client:
        for i, query in enumerate(QUERIES):
            print(f"\n{'='*60}")
            print(f"[{i+1}/{len(QUERIES)}] Query: {query}")
            print(f"{'='*60}")

            items, approach = scrape_query(client, query)
            approach_summary[query] = approach

            all_results[query] = items
            total_count += len(items)

            print(f"  => {approach}: {len(items)} items")
            if items:
                sample = items[0]
                print(f"  Sample: {sample['title'][:60]}  ¥{sample['price']:,}  {sample['condition']}")

            if i < len(QUERIES) - 1:
                delay()

    # Build output
    output = {
        "scraped_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "total_items": total_count,
        "approach_summary": approach_summary,
        "note": "Mercari API requires authentication for sold items. SSR via Googlebot UA returns on-sale listings (status=ITEM_STATUS_ON_SALE) which provide current market asking prices. Sold-item data requires Playwright or authenticated API access.",
        "queries": {},
    }
    for q in QUERIES:
        items = all_results.get(q, [])
        output["queries"][q] = {
            "count": len(items),
            "items": items,
        }

    OUTPUT_FILE.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")

    # Summary
    print(f"\n{'='*60}")
    print(f"SCRAPING COMPLETE")
    print(f"{'='*60}")
    print(f"Total items scraped: {total_count}")
    print(f"Output: {OUTPUT_FILE}")
    print(f"\nPer-query results:")
    for q in QUERIES:
        items = all_results.get(q, [])
        approach = approach_summary.get(q, "?")
        prices = [it["price"] for it in items if it["price"] > 0]
        if prices:
            print(f"  {q}: {len(items)} items, approach={approach}, "
                  f"price range=¥{min(prices):,} - ¥{max(prices):,}, "
                  f"median=¥{sorted(prices)[len(prices)//2]:,}")
        else:
            print(f"  {q}: {len(items)} items, approach={approach}")


if __name__ == "__main__":
    main()
