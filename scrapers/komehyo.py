"""Komehyo (コメ兵) scraper for ResaleLens."""

import logging
import re
from typing import Optional

from bs4 import BeautifulSoup

from .base import BaseScraper, ScrapedItem

logger = logging.getLogger(__name__)


class KomehyoScraper(BaseScraper):
    """Scrape product listings from Komehyo online store."""

    SOURCE_NAME = "komehyo"
    BASE_URL = "https://komehyo.jp"
    MIN_DELAY = 2.0
    MAX_DELAY = 4.0

    async def scrape_brand(self, brand: str, model: str, item_type: str = "bag") -> list[ScrapedItem]:
        """Scrape Komehyo listings for current selling prices."""
        items = []
        query = f"{brand} {model}"

        search_url = f"{self.BASE_URL}/search"
        params = {"keyword": query}

        response = await self._fetch(search_url, params=params)
        if not response:
            return items

        soup = BeautifulSoup(response.text, "html.parser")

        for listing in soup.select(".item-list__item"):
            try:
                title_el = listing.select_one(".item-list__item-name")
                price_el = listing.select_one(".item-list__item-price")
                condition_el = listing.select_one(".item-list__item-rank")
                link_el = listing.select_one("a")

                if not title_el or not price_el:
                    continue

                title = title_el.get_text(strip=True)
                price = self._parse_price(price_el.get_text(strip=True))
                condition = condition_el.get_text(strip=True) if condition_el else None
                url = self.BASE_URL + link_el.get("href", "") if link_el else None

                if price > 0:
                    items.append(ScrapedItem(
                        product_name=title,
                        brand=brand,
                        model=model,
                        price=price,
                        condition=condition,
                        listing_url=url,
                        source=self.SOURCE_NAME,
                        item_type=item_type,
                    ))
            except Exception as e:
                logger.warning(f"Error parsing Komehyo listing: {e}")

        logger.info(f"Komehyo: found {len(items)} items for '{query}'")
        return items

    def _parse_price(self, price_text: str) -> int:
        cleaned = re.sub(r'[¥,\s円税込]', '', price_text)
        try:
            return int(cleaned)
        except ValueError:
            return 0
