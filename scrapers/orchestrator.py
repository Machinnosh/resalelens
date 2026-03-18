"""Scraping orchestrator - coordinates all scrapers and saves to Supabase."""

import asyncio
import logging
import os
from datetime import datetime

from supabase import create_client

from .base import ScrapedItem
from .mercari_playwright import MercariPlaywrightScraper
from .yahoo_auction import YahooAuctionScraper
from .rakuma import RakumaScraper
from .komehyo import KomehyoScraper
from .daikokuya import DaikokuyaScraper
from .brandear import BrandearScraper
from .matching import match_product

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Supabase client for server-side operations
SUPABASE_URL = os.environ.get("EXPO_PUBLIC_SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")


def get_supabase():
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        raise RuntimeError("Supabase credentials not set. Set EXPO_PUBLIC_SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.")
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


# Queries to scrape - brand/model combinations for all Tier 1 brands
SCRAPE_QUERIES = [
    # Hermès
    {"brand": "エルメス", "model": "バーキン", "item_type": "bag"},
    {"brand": "エルメス", "model": "ケリー", "item_type": "bag"},
    {"brand": "エルメス", "model": "ピコタン", "item_type": "bag"},
    {"brand": "エルメス", "model": "コンスタンス", "item_type": "bag"},
    {"brand": "エルメス", "model": "ベアン 財布", "item_type": "wallet"},
    # CHANEL
    {"brand": "シャネル", "model": "マトラッセ チェーンショルダー", "item_type": "bag"},
    {"brand": "シャネル", "model": "ボーイシャネル", "item_type": "bag"},
    {"brand": "シャネル", "model": "マトラッセ 財布", "item_type": "wallet"},
    # Louis Vuitton
    {"brand": "ルイヴィトン", "model": "ネヴァーフル", "item_type": "bag"},
    {"brand": "ルイヴィトン", "model": "スピーディ", "item_type": "bag"},
    {"brand": "ルイヴィトン", "model": "アルマ", "item_type": "bag"},
    {"brand": "ルイヴィトン", "model": "ジッピーウォレット", "item_type": "wallet"},
    # Rolex
    {"brand": "ロレックス", "model": "サブマリーナ", "item_type": "watch"},
    {"brand": "ロレックス", "model": "デイトナ", "item_type": "watch"},
    {"brand": "ロレックス", "model": "デイトジャスト", "item_type": "watch"},
    {"brand": "ロレックス", "model": "GMTマスター", "item_type": "watch"},
    # Omega
    {"brand": "オメガ", "model": "スピードマスター", "item_type": "watch"},
    {"brand": "オメガ", "model": "シーマスター", "item_type": "watch"},
    # Cartier
    {"brand": "カルティエ", "model": "タンク", "item_type": "watch"},
    {"brand": "カルティエ", "model": "サントス", "item_type": "watch"},
    {"brand": "カルティエ", "model": "バロンブルー", "item_type": "watch"},
]


async def run_scraper(scraper_class, queries: list[dict]) -> list[ScrapedItem]:
    """Run a single scraper with error handling."""
    try:
        async with scraper_class() as scraper:
            return await scraper.scrape_all(queries)
    except Exception as e:
        logger.error(f"Scraper {scraper_class.__name__} failed: {e}")
        return []


def save_to_supabase(items: list[ScrapedItem]):
    """Save scraped items to Supabase resale_transactions table."""
    if not items:
        logger.info("No items to save")
        return

    supabase = get_supabase()

    # Load product mapping from DB
    products_resp = supabase.table("products").select("id, brand_id, model, size, item_type").execute()
    brands_resp = supabase.table("brands").select("id, slug").execute()

    brand_map = {b["slug"]: b["id"] for b in brands_resp.data}
    product_lookup = {}
    for p in products_resp.data:
        key = f"{p['brand_id']}:{p['model']}:{p.get('size', '')}"
        product_lookup[key] = p["id"]

    saved = 0
    skipped = 0

    for item in items:
        match = match_product(item.product_name, brand_hint=None)
        if not match:
            skipped += 1
            continue

        brand_id = brand_map.get(match.brand_slug)
        if not brand_id:
            skipped += 1
            continue

        # Find product ID
        product_id = None
        for key, pid in product_lookup.items():
            if key.startswith(f"{brand_id}:{match.model_slug}"):
                if match.size and match.size in key:
                    product_id = pid
                    break
                elif not product_id:
                    product_id = pid

        if not product_id:
            skipped += 1
            continue

        try:
            supabase.table("resale_transactions").insert({
                "product_id": product_id,
                "source": item.source,
                "sold_price": item.price,
                "condition": item.condition or match.condition,
                "sold_date": (item.sold_date or datetime.now()).strftime("%Y-%m-%d"),
                "listing_url": item.listing_url,
                "raw_data": item.raw_data,
            }).execute()
            saved += 1
        except Exception as e:
            logger.warning(f"Failed to save item: {e}")

    logger.info(f"Saved {saved} items, skipped {skipped} items")


async def run_daily_scrape():
    """Run the full daily scraping pipeline."""
    logger.info("=== Starting daily scrape ===")
    all_items: list[ScrapedItem] = []

    # Run httpx-based scrapers concurrently
    httpx_tasks = [
        run_scraper(YahooAuctionScraper, SCRAPE_QUERIES),
        run_scraper(KomehyoScraper, SCRAPE_QUERIES),
        run_scraper(DaikokuyaScraper, SCRAPE_QUERIES),
        run_scraper(BrandearScraper, SCRAPE_QUERIES),
    ]
    httpx_results = await asyncio.gather(*httpx_tasks)
    for result in httpx_results:
        all_items.extend(result)

    # Run Playwright-based scrapers sequentially (browser resource heavy)
    mercari_items = await run_scraper(MercariPlaywrightScraper, SCRAPE_QUERIES)
    all_items.extend(mercari_items)

    rakuma_items = await run_scraper(RakumaScraper, SCRAPE_QUERIES)
    all_items.extend(rakuma_items)

    logger.info(f"Total scraped items: {len(all_items)}")

    # Save to Supabase
    save_to_supabase(all_items)

    logger.info("=== Daily scrape complete ===")
    return len(all_items)


if __name__ == "__main__":
    asyncio.run(run_daily_scrape())
