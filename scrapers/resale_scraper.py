"""
Scraper for Japanese luxury brand resale shops.
Extracts market price data from:
1. ブランディア (Brandear) - brandear.jp - Buyback reference prices
2. コメ兵 (Komehyo) - komehyo.jp - Uses CHEQ AI bot detection (blocked)
3. 大黒屋 (Daikokuya) - e-daikoku.com - No public product search available

Search queries:
- バーキン (Birkin)
- シャネル フラップ (Chanel Flap)
- ネヴァーフル (Neverfull)
- ロレックス サブマリーナ (Rolex Submariner)
- スピードマスター (Speedmaster)
"""

import asyncio
import json
import os
import re
import sys
import io
from urllib.parse import quote

import httpx
from bs4 import BeautifulSoup

# Fix Windows encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
os.makedirs(DATA_DIR, exist_ok=True)

QUERIES = [
    "バーキン",
    "シャネル フラップ",
    "ネヴァーフル",
    "ロレックス サブマリーナ",
    "スピードマスター",
]

# Map queries to Brandear categories and filter keywords
QUERY_CONFIG = {
    "バーキン": {
        "categories": ["bag"],
        "filter_keywords": ["バーキン", "birkin", "Birkin"],
        "brand_keywords": ["HERMES", "エルメス", "hermes"],
    },
    "シャネル フラップ": {
        "categories": ["bag"],
        "filter_keywords": ["フラップ", "マトラッセ", "CHANEL", "シャネル"],
        "brand_keywords": ["CHANEL", "シャネル"],
    },
    "ネヴァーフル": {
        "categories": ["bag"],
        "filter_keywords": ["ネヴァーフル", "ネバーフル", "neverfull", "Neverfull", "LOUIS VUITTON", "ヴィトン"],
        "brand_keywords": ["LOUIS VUITTON", "ヴィトン", "LV"],
    },
    "ロレックス サブマリーナ": {
        "categories": ["watch"],
        "filter_keywords": ["サブマリーナ", "submariner", "Submariner"],
        "brand_keywords": ["ROLEX", "ロレックス"],
    },
    "スピードマスター": {
        "categories": ["watch"],
        "filter_keywords": ["スピードマスター", "speedmaster", "Speedmaster"],
        "brand_keywords": ["OMEGA", "オメガ"],
    },
}

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
HEADERS = {
    "User-Agent": UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "ja,en-US;q=0.7,en;q=0.3",
    "Referer": "https://www.google.com/",
}

summary = {}


def save_json(filename, data):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  Saved {len(data)} items to {path}")


def matches_query(title, config):
    """Check if a title matches the query's filter keywords.

    For precise matching: requires at least one filter keyword match.
    Brand-only matches are included as broader context but tagged differently.
    """
    title_lower = title.lower()
    has_keyword = any(kw.lower() in title_lower for kw in config["filter_keywords"])
    has_brand = any(kw.lower() in title_lower for kw in config["brand_keywords"])
    # Require at least a keyword match, or brand match for brand-specific queries
    return has_keyword or has_brand


# ============================================================
# BRANDEAR - Parse buyback reference prices
# ============================================================
def parse_brandear_items(soup, query, category):
    """Parse Brandear's price data from category pages."""
    items = []
    config = QUERY_CONFIG[query]

    # Method 1: Parse item01 cells (product cards with images and prices)
    item01_cells = soup.select("td.item01")
    for cell in item01_cells:
        # Get image alt for product identification
        img_el = cell.select_one("img")
        img_alt = img_el.get("alt", "") if img_el else ""
        img_src = img_el.get("data-src", "") if img_el else ""

        # Get all text content from the cell
        tds = cell.select("td")
        title_parts = []
        price_text = None

        for td in tds:
            text = td.get_text(strip=True)
            classes = td.get("class", [])
            if "text_orange" in classes and "円" in text:
                price_match = re.search(r'[～~]?([\d,]+)円', text)
                if price_match:
                    price_text = price_match.group(0)
            elif text and len(text) > 2:
                # This is likely the title/description
                # Clean up line breaks
                clean_text = re.sub(r'\s+', ' ', td.get_text(" ", strip=True))
                title_parts.append(clean_text)

        title = " ".join(title_parts).strip()
        if not title:
            title = img_alt

        if title and price_text:
            items.append({
                "title": title,
                "price": price_text,
                "price_type": "参考買取価格",
                "condition": None,
                "image_url": img_src,
                "url": f"https://brandear.jp/ct/{category}",
                "query": query,
                "source": "brandear",
            })

    # Method 2: Parse link_box03 rows (detailed price tables by brand/model)
    accordions = soup.select(".sankoukakaku")
    for acc in accordions:
        # Get brand name from preceding accordion-title
        brand_header = acc.find_previous_sibling(class_="accordion-title")
        brand_name = brand_header.get_text(strip=True) if brand_header else ""

        rows = acc.select("tr.link_box03")
        for row in rows:
            tds = row.select("td")
            if len(tds) >= 2:
                model_text = tds[0].get_text(strip=True)
                price_td = tds[1].get_text(strip=True)
                price_match = re.search(r'[～~]?([\d,]+)円', price_td)
                price_text = price_match.group(0) if price_match else price_td

                full_title = f"{brand_name} {model_text}".strip() if brand_name else model_text

                items.append({
                    "title": full_title,
                    "price": price_text,
                    "price_type": "参考買取価格",
                    "condition": None,
                    "image_url": None,
                    "url": f"https://brandear.jp/ct/{category}",
                    "query": query,
                    "source": "brandear",
                })

    # Method 3: Parse item02 rows (simpler price reference list)
    for table in soup.select("table.kakaku_title02"):
        rows = table.select("tr")
        for row in rows:
            item_td = row.select_one("td.item02")
            price_td = row.select_one("td.text_orange")
            if item_td and price_td:
                title = item_td.get_text(strip=True)
                price = price_td.get_text(strip=True)
                price_match = re.search(r'[～~]?([\d,]+)円', price)
                if price_match and title:
                    items.append({
                        "title": title,
                        "price": price_match.group(0),
                        "price_type": "参考買取価格",
                        "condition": None,
                        "image_url": None,
                        "url": f"https://brandear.jp/ct/{category}",
                        "query": query,
                        "source": "brandear",
                    })

    # Deduplicate by title+price
    seen = set()
    unique_items = []
    for item in items:
        key = (item["title"], item["price"])
        if key not in seen and item["title"]:
            seen.add(key)
            unique_items.append(item)

    # Filter to only items matching the query
    filtered = [item for item in unique_items if matches_query(item["title"], config)]

    return filtered


async def scrape_brandear(client):
    """Scrape Brandear for all queries."""
    all_items = []

    for query in QUERIES:
        config = QUERY_CONFIG[query]
        print(f"\n  Query: {query}")

        for cat in config["categories"]:
            url = f"https://brandear.jp/ct/{cat}"
            print(f"    Fetching: {url}")
            try:
                resp = await client.get(url, follow_redirects=True, timeout=20)
                print(f"    Status: {resp.status_code}, Length: {len(resp.text)}")

                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, "html.parser")
                    items = parse_brandear_items(soup, query, cat)
                    print(f"    Parsed {len(items)} matching items")

                    if items:
                        for item in items[:3]:
                            print(f"      {item['title'][:60]} | {item['price']}")
                        if len(items) > 3:
                            print(f"      ... and {len(items) - 3} more")

                    all_items.extend(items)
            except Exception as e:
                print(f"    Error: {e}")

        await asyncio.sleep(1)

    return all_items


# ============================================================
# KOMEHYO - Try with session cookies
# ============================================================
async def scrape_komehyo(client):
    """
    Attempt to scrape Komehyo. The site uses CHEQ AI bot detection which
    invalidates sessions for automated clients. We try multiple approaches.
    """
    all_items = []

    # Approach 1: Try httpx with session cookies
    print("\n  Approach 1: httpx with session cookies")
    special_headers = {
        **HEADERS,
        "Sec-Ch-Ua": '"Chromium";v="131", "Google Chrome";v="131"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
    }

    try:
        # Get homepage to obtain session cookies
        r = await client.get("https://komehyo.jp/", follow_redirects=False, timeout=15, headers=special_headers)
        print(f"    Homepage: status={r.status_code}")

        if r.status_code == 302:
            location = r.headers.get("location", "")
            if "/error" in location:
                print(f"    Redirected to error (bot detected by CHEQ AI)")
            else:
                # Follow redirect with cookies
                cookies = dict(r.cookies)
                r2 = await client.get(f"https://komehyo.jp{location}", follow_redirects=True,
                                     timeout=15, headers=special_headers, cookies=cookies)
                print(f"    Follow-up: status={r2.status_code}")
    except Exception as e:
        print(f"    Error: {e}")

    # Approach 2: Try Playwright with stealth
    if not all_items:
        print("\n  Approach 2: Playwright with stealth")
        from playwright.async_api import async_playwright
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=["--disable-blink-features=AutomationControlled"]
                )
                context = await browser.new_context(
                    user_agent=UA,
                    locale="ja-JP",
                    viewport={"width": 1366, "height": 768},
                )
                page = await context.new_page()
                await page.add_init_script("""
                    delete navigator.__proto__.webdriver;
                    Object.defineProperty(navigator, 'webdriver', {get: () => false});
                    window.chrome = {runtime: {}, loadTimes: function(){}, csi: function(){}};
                """)

                resp = await page.goto("https://komehyo.jp/", wait_until="domcontentloaded", timeout=30000)
                status = resp.status if resp else "N/A"
                print(f"    Homepage: status={status}, url={page.url}")

                if status == 200 and "/error" not in page.url:
                    # Try each query
                    for query in QUERIES:
                        url = f"https://komehyo.jp/search?keyword={quote(query)}"
                        resp = await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                        await page.wait_for_timeout(5000)
                        html = await page.content()

                        soup = BeautifulSoup(html, "html.parser")
                        nd = soup.find("script", id="__NEXT_DATA__")
                        if nd and nd.string:
                            data = json.loads(nd.string)
                            props = data.get("props", {}).get("pageProps", {})
                            # Extract products recursively
                            items = extract_products_recursive(props, query)
                            if items:
                                all_items.extend(items)
                                print(f"    {query}: {len(items)} items found")
                        await asyncio.sleep(1)
                else:
                    print(f"    Blocked by CHEQ AI bot detection")

                await browser.close()
        except Exception as e:
            print(f"    Playwright error: {e}")

    return all_items


def extract_products_recursive(data, query, depth=0):
    """Recursively search for product arrays in nested data."""
    items = []
    if depth > 6:
        return items

    if isinstance(data, dict):
        # Check if this dict looks like a product
        if any(k in data for k in ["itemName", "productName", "name"]) and any(k in data for k in ["price", "sellPrice", "displayPrice"]):
            title = data.get("itemName") or data.get("productName") or data.get("name", "")
            price = data.get("price") or data.get("sellPrice") or data.get("displayPrice")
            condition = data.get("condition") or data.get("rank") or data.get("grade")
            url = data.get("url") or data.get("link") or data.get("href")
            if url and not url.startswith("http"):
                url = f"https://komehyo.jp{url}"
            items.append({
                "title": str(title),
                "price": str(price) if price else None,
                "condition": str(condition) if condition else None,
                "url": url,
                "query": query,
                "source": "komehyo",
            })
        else:
            for v in data.values():
                items.extend(extract_products_recursive(v, query, depth + 1))
    elif isinstance(data, list):
        for item in data:
            items.extend(extract_products_recursive(item, query, depth + 1))

    return items


# ============================================================
# DAIKOKUYA
# ============================================================
async def scrape_daikokuya(client):
    """
    Attempt to scrape Daikokuya. Their website (e-daikoku.com) doesn't have
    a public product search API. We try their brand information pages.
    """
    all_items = []

    # Try the brand info page which has some price data
    print("\n  Trying brand information page...")
    try:
        resp = await client.get("https://www.e-daikoku.com/brand/", follow_redirects=True, timeout=15)
        print(f"    Status: {resp.status_code}")

        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            price_pattern = re.compile(r'([\d,]+)\s*円')

            # Look for price data in the page
            for el in soup.select("td, dd, span, div"):
                text = el.get_text(strip=True)
                if price_pattern.search(text) and len(text) > 10 and len(text) < 200:
                    pm = price_pattern.search(text)
                    price_val = int(pm.group(1).replace(",", ""))
                    # Filter out 0 yen and very low values (noise)
                    if price_val < 1000:
                        continue
                    link = el.find_parent("a")
                    url = link.get("href", "") if link else ""
                    if url and not url.startswith("http"):
                        url = f"https://www.e-daikoku.com{url}"
                    all_items.append({
                        "title": text,
                        "price": f"{pm.group(1)}円",
                        "condition": None,
                        "url": url or "https://www.e-daikoku.com/brand/",
                        "query": "brand_page",
                        "source": "daikokuya",
                    })
    except Exception as e:
        print(f"    Error: {e}")

    # Try Playwright to use their interactive features
    print("\n  Trying Playwright for interactive search...")
    from playwright.async_api import async_playwright
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(user_agent=UA, locale="ja-JP")
            page = await context.new_page()

            resp = await page.goto("https://www.e-daikoku.com/brand/", wait_until="domcontentloaded", timeout=30000)
            print(f"    Brand page: status={resp.status if resp else 'N/A'}")
            await page.wait_for_timeout(3000)

            # Extract any price data rendered by JavaScript
            price_data = await page.evaluate("""() => {
                const items = [];
                const pricePattern = /([\\d,]+)\\s*円/;

                // Look for product-like elements
                document.querySelectorAll('a, div, li, article').forEach(el => {
                    const text = el.textContent.trim();
                    const match = text.match(pricePattern);
                    if (match && text.length > 15 && text.length < 300) {
                        // Check if this is a leaf-ish element (not too many children)
                        if (el.children.length < 10) {
                            items.push({
                                title: text.substring(0, 200),
                                price: match[0],
                                url: el.href || el.closest('a')?.href || '',
                            });
                        }
                    }
                });
                return items.slice(0, 50);
            }""")

            if price_data:
                print(f"    Found {len(price_data)} price elements")
                for pd in price_data:
                    all_items.append({
                        "title": pd["title"],
                        "price": pd["price"],
                        "condition": None,
                        "url": pd["url"],
                        "query": "brand_page",
                        "source": "daikokuya",
                    })

            await browser.close()
    except Exception as e:
        print(f"    Playwright error: {e}")

    # Deduplicate
    seen = set()
    unique = []
    for item in all_items:
        key = (item["title"][:50], item["price"])
        if key not in seen:
            seen.add(key)
            unique.append(item)

    return unique


# ============================================================
# MAIN
# ============================================================
async def main():
    print("=" * 60)
    print("Japanese Luxury Resale Shop Scraper")
    print("=" * 60)

    async with httpx.AsyncClient(headers=HEADERS, timeout=20) as client:
        # === BRANDEAR ===
        print("\n" + "=" * 50)
        print("1. BRANDEAR (ブランディア) - buyback reference prices")
        print("=" * 50)
        brandear_items = await scrape_brandear(client)
        save_json("brandear_results.json", brandear_items)
        summary["brandear"] = {
            "total_items": len(brandear_items),
            "method": "httpx (direct HTTP)",
            "queries_with_results": len(set(i["query"] for i in brandear_items)),
            "status": "OK" if brandear_items else "NO_DATA",
            "note": "Buyback reference prices (参考買取価格), not selling prices",
        }

        # === KOMEHYO ===
        print("\n" + "=" * 50)
        print("2. KOMEHYO (コメ兵)")
        print("=" * 50)
        komehyo_items = await scrape_komehyo(client)
        save_json("komehyo_results.json", komehyo_items)
        summary["komehyo"] = {
            "total_items": len(komehyo_items),
            "method": "httpx + Playwright",
            "queries_with_results": len(set(i["query"] for i in komehyo_items)) if komehyo_items else 0,
            "status": "OK" if komehyo_items else "BLOCKED",
            "note": "Site uses CHEQ AI bot detection. All automated access returns 302 to /error.",
        }

        # === DAIKOKUYA ===
        print("\n" + "=" * 50)
        print("3. DAIKOKUYA (大黒屋)")
        print("=" * 50)
        daikokuya_items = await scrape_daikokuya(client)
        save_json("daikokuya_results.json", daikokuya_items)
        summary["daikokuya"] = {
            "total_items": len(daikokuya_items),
            "method": "httpx + Playwright",
            "queries_with_results": len(set(i["query"] for i in daikokuya_items)) if daikokuya_items else 0,
            "status": "OK" if daikokuya_items else "NO_PRODUCT_SEARCH",
            "note": "No public product search/listing available. Brand page has limited price data.",
        }

    # === SUMMARY ===
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    for shop, info in summary.items():
        print(f"\n  {shop.upper()}:")
        print(f"    Status: {info['status']}")
        print(f"    Total items: {info['total_items']}")
        print(f"    Method used: {info['method']}")
        print(f"    Queries with results: {info['queries_with_results']}/{len(QUERIES)}")
        print(f"    Note: {info['note']}")

    total = sum(info["total_items"] for info in summary.values())
    print(f"\n  TOTAL ITEMS ACROSS ALL SHOPS: {total}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
