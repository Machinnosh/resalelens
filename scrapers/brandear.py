"""Brandear (ブランディア) scraper for ResaleLens - buy prices."""

import logging
import re
from typing import Optional

from bs4 import BeautifulSoup

from .base import BaseScraper, ScrapedItem

logger = logging.getLogger(__name__)


class BrandearScraper(BaseScraper):
    """Scrape buy (kaitori) prices from Brandear."""

    SOURCE_NAME = "brandear"
    BASE_URL = "https://brandear.jp"
    MIN_DELAY = 2.0
    MAX_DELAY = 4.0

    async def scrape_brand(self, brand: str, model: str, item_type: str = "bag") -> list[ScrapedItem]:
        """Scrape Brandear buy price listings."""
        items = []
        query = f"{brand} {model}"

        search_url = f"{self.BASE_URL}/ct/search"
        params = {"keyword": query}

        response = await self._fetch(search_url, params=params)
        if not response:
            return items

        soup = BeautifulSoup(response.text, "html.parser")

        for listing in soup.select(".item-list-item, .search-item, .product-card"):
            try:
                title_el = listing.select_one(".item-name, .product-title, h3")
                price_el = listing.select_one(".kaitori-price, .price, .buy-price")
                link_el = listing.select_one("a")

                if not title_el or not price_el:
                    continue

                title = title_el.get_text(strip=True)
                price = self._parse_price(price_el.get_text(strip=True))

                url = ""
                if link_el:
                    href = link_el.get("href", "")
                    url = f"{self.BASE_URL}{href}" if href.startswith("/") else href

                if price > 0:
                    items.append(ScrapedItem(
                        product_name=title,
                        brand=brand,
                        model=model,
                        price=price,
                        listing_url=url,
                        source=self.SOURCE_NAME,
                        item_type=item_type,
                        raw_data={"title": title, "price_type": "buy"},
                    ))
            except Exception as e:
                logger.warning(f"Error parsing Brandear listing: {e}")

        logger.info(f"Brandear: found {len(items)} items for '{query}'")
        return items

    def _parse_price(self, price_text: str) -> int:
        cleaned = re.sub(r"[¥,\s円~～約]", "", price_text)
        # Handle range prices (take the higher end)
        if "-" in cleaned:
            parts = cleaned.split("-")
            cleaned = parts[-1]
        try:
            return int(cleaned)
        except ValueError:
            return 0
