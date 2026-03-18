"""Base scraper class for ResaleLens data collection."""

import asyncio
import logging
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

import httpx

logger = logging.getLogger(__name__)


@dataclass
class ScrapedItem:
    """A single scraped resale transaction."""
    product_name: str
    brand: str
    model: str
    price: int
    condition: Optional[str] = None
    sold_date: Optional[datetime] = None
    listing_url: Optional[str] = None
    source: str = ""
    size: Optional[str] = None
    material: Optional[str] = None
    item_type: str = "bag"  # bag, wallet, watch
    raw_data: dict = field(default_factory=dict)


class BaseScraper(ABC):
    """Base class for all ResaleLens scrapers."""

    SOURCE_NAME: str = ""
    BASE_URL: str = ""
    MIN_DELAY: float = 2.0
    MAX_DELAY: float = 5.0
    MAX_RETRIES: int = 3

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0",
    ]

    def __init__(self):
        self.client: Optional[httpx.AsyncClient] = None
        self.items: list[ScrapedItem] = []

    async def __aenter__(self):
        self.client = httpx.AsyncClient(
            headers={"User-Agent": random.choice(self.USER_AGENTS)},
            timeout=30.0,
            follow_redirects=True,
        )
        return self

    async def __aexit__(self, *args):
        if self.client:
            await self.client.aclose()

    async def _delay(self):
        """Random delay between requests."""
        await asyncio.sleep(random.uniform(self.MIN_DELAY, self.MAX_DELAY))

    async def _fetch(self, url: str, **kwargs) -> Optional[httpx.Response]:
        """Fetch URL with retry logic."""
        for attempt in range(self.MAX_RETRIES):
            try:
                await self._delay()
                response = await self.client.get(url, **kwargs)
                if response.status_code == 429:
                    wait = 2 ** (attempt + 2)
                    logger.warning(f"Rate limited, waiting {wait}s")
                    await asyncio.sleep(wait)
                    continue
                response.raise_for_status()
                return response
            except httpx.HTTPError as e:
                logger.warning(f"Attempt {attempt + 1}/{self.MAX_RETRIES} failed: {e}")
                if attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(2 ** attempt)
        return None

    @abstractmethod
    async def scrape_brand(self, brand: str, model: str, item_type: str = "bag") -> list[ScrapedItem]:
        """Scrape transactions for a specific brand/model."""
        ...

    async def scrape_all(self, queries: list[dict]) -> list[ScrapedItem]:
        """Scrape multiple brand/model combinations."""
        all_items = []
        for query in queries:
            try:
                items = await self.scrape_brand(
                    brand=query["brand"],
                    model=query["model"],
                    item_type=query.get("item_type", "bag"),
                )
                all_items.extend(items)
                logger.info(f"[{self.SOURCE_NAME}] {query['brand']} {query['model']}: {len(items)} items")
            except Exception as e:
                logger.error(f"[{self.SOURCE_NAME}] Error scraping {query}: {e}")
        self.items = all_items
        return all_items
