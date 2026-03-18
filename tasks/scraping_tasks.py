"""Celery tasks for scheduled scraping."""

import asyncio
import logging
import os

from celery import Celery
from celery.schedules import crontab

logger = logging.getLogger(__name__)

# Celery configuration
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

app = Celery("resalelens", broker=REDIS_URL, backend=REDIS_URL)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Tokyo",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max per task
    task_soft_time_limit=3000,  # 50 min soft limit
)

# Schedule: runs every day at specified times (JST)
app.conf.beat_schedule = {
    "daily-mercari-scrape": {
        "task": "tasks.scraping_tasks.scrape_mercari",
        "schedule": crontab(hour=3, minute=0),  # 03:00 JST
    },
    "daily-yahoo-scrape": {
        "task": "tasks.scraping_tasks.scrape_yahoo",
        "schedule": crontab(hour=4, minute=0),  # 04:00 JST
    },
    "daily-rakuma-scrape": {
        "task": "tasks.scraping_tasks.scrape_rakuma",
        "schedule": crontab(hour=4, minute=30),  # 04:30 JST
    },
    "weekly-shops-scrape": {
        "task": "tasks.scraping_tasks.scrape_shops",
        "schedule": crontab(hour=5, minute=0, day_of_week=1),  # Monday 05:00 JST
    },
    "weekly-ml-retrain": {
        "task": "tasks.ml_tasks.retrain_model",
        "schedule": crontab(hour=6, minute=0, day_of_week=1),  # Monday 06:00 JST
    },
}


@app.task(name="tasks.scraping_tasks.scrape_mercari")
def scrape_mercari():
    """Scrape Mercari sold listings."""
    from scrapers.mercari_playwright import MercariPlaywrightScraper
    from scrapers.orchestrator import SCRAPE_QUERIES, run_scraper, save_to_supabase

    logger.info("Starting Mercari scrape task")
    items = asyncio.run(run_scraper(MercariPlaywrightScraper, SCRAPE_QUERIES))
    save_to_supabase(items)
    return {"source": "mercari", "items_count": len(items)}


@app.task(name="tasks.scraping_tasks.scrape_yahoo")
def scrape_yahoo():
    """Scrape Yahoo Auctions completed listings."""
    from scrapers.yahoo_auction import YahooAuctionScraper
    from scrapers.orchestrator import SCRAPE_QUERIES, run_scraper, save_to_supabase

    logger.info("Starting Yahoo Auction scrape task")
    items = asyncio.run(run_scraper(YahooAuctionScraper, SCRAPE_QUERIES))
    save_to_supabase(items)
    return {"source": "yahoo_auction", "items_count": len(items)}


@app.task(name="tasks.scraping_tasks.scrape_rakuma")
def scrape_rakuma():
    """Scrape Rakuma sold listings."""
    from scrapers.rakuma import RakumaScraper
    from scrapers.orchestrator import SCRAPE_QUERIES, run_scraper, save_to_supabase

    logger.info("Starting Rakuma scrape task")
    items = asyncio.run(run_scraper(RakumaScraper, SCRAPE_QUERIES))
    save_to_supabase(items)
    return {"source": "rakuma", "items_count": len(items)}


@app.task(name="tasks.scraping_tasks.scrape_shops")
def scrape_shops():
    """Scrape shop prices (Komehyo, Daikokuya, Brandear)."""
    from scrapers.komehyo import KomehyoScraper
    from scrapers.daikokuya import DaikokuyaScraper
    from scrapers.brandear import BrandearScraper
    from scrapers.orchestrator import SCRAPE_QUERIES, run_scraper, save_to_supabase

    logger.info("Starting shop scrape task")
    all_items = []
    for scraper_cls in [KomehyoScraper, DaikokuyaScraper, BrandearScraper]:
        items = asyncio.run(run_scraper(scraper_cls, SCRAPE_QUERIES))
        all_items.extend(items)

    save_to_supabase(all_items)
    return {"source": "shops", "items_count": len(all_items)}


@app.task(name="tasks.scraping_tasks.run_full_scrape")
def run_full_scrape():
    """Run all scrapers (manual trigger)."""
    from scrapers.orchestrator import run_daily_scrape

    logger.info("Starting full scrape (manual)")
    count = asyncio.run(run_daily_scrape())
    return {"total_items": count}
