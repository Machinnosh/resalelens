"""Mercari scraper for ResaleLens - uses Playwright for SPA rendering."""

import logging
import re
from datetime import datetime
from typing import Optional

from .base import BaseScraper, ScrapedItem

logger = logging.getLogger(__name__)


class MercariScraper(BaseScraper):
    """Scrape sold listings from Mercari."""

    SOURCE_NAME = "mercari"
    BASE_URL = "https://jp.mercari.com"
    MIN_DELAY = 3.0
    MAX_DELAY = 6.0

    async def scrape_brand(self, brand: str, model: str, item_type: str = "bag") -> list[ScrapedItem]:
        """
        Scrape Mercari sold listings for a brand/model.

        Mercari is a SPA - requires Playwright for full rendering.
        MVP approach: use Mercari's search API endpoint directly.
        """
        items = []
        query = f"{brand} {model}"

        # Mercari search API (sold items)
        # status=sold_out for completed transactions
        search_url = f"{self.BASE_URL}/search"
        params = {
            "keyword": query,
            "status": "sold_out",
            "sort": "created_time",
            "order": "desc",
            "category_id": self._get_category_id(item_type),
        }

        response = await self._fetch(search_url, params=params)
        if not response:
            return items

        # Parse results - actual implementation depends on Mercari's response format
        # For MVP, we'll use Playwright-based scraping
        # This is a placeholder that will be replaced with actual Playwright logic
        logger.info(f"Mercari search for '{query}' - response status: {response.status_code}")

        return items

    def _get_category_id(self, item_type: str) -> str:
        """Map item type to Mercari category ID."""
        categories = {
            "bag": "4",       # レディースバッグ
            "wallet": "65",   # 財布
            "watch": "107",   # 腕時計
        }
        return categories.get(item_type, "4")

    def _parse_price(self, price_text: str) -> int:
        """Parse Mercari price string to integer."""
        cleaned = re.sub(r'[¥,\s円]', '', price_text)
        try:
            return int(cleaned)
        except ValueError:
            return 0

    def _parse_date(self, date_text: str) -> Optional[datetime]:
        """Parse Mercari date string."""
        try:
            return datetime.fromisoformat(date_text)
        except (ValueError, TypeError):
            return None
