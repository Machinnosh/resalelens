"""Daikokuya (大黒屋) scraper for ResaleLens - buy/sell prices."""

import logging
import re
from typing import Optional

from bs4 import BeautifulSoup

from .base import BaseScraper, ScrapedItem

logger = logging.getLogger(__name__)


class DaikokuyaScraper(BaseScraper):
    """Scrape buy/sell prices from Daikokuya."""

    SOURCE_NAME = "daikokuya"
    BASE_URL = "https://www.e-daikoku.com"
    MIN_DELAY = 2.0
    MAX_DELAY = 4.0

    async def scrape_brand(self, brand: str, model: str, item_type: str = "bag") -> list[ScrapedItem]:
        """Scrape Daikokuya listings for buy/sell prices."""
        items = []
        query = f"{brand} {model}"

        search_url = f"{self.BASE_URL}/search"
        params = {"q": query}

        response = await self._fetch(search_url, params=params)
        if not response:
            return items

        soup = BeautifulSoup(response.text, "html.parser")

        for listing in soup.select(".product-item, .item-card, .search-result-item"):
            try:
                title_el = listing.select_one(".product-name, .item-name, h3, .title")
                buy_price_el = listing.select_one(".buy-price, .kaitori-price")
                sell_price_el = listing.select_one(".sell-price, .販売価格, .price")
                link_el = listing.select_one("a")

                if not title_el:
                    continue

                title = title_el.get_text(strip=True)

                # Prefer sell price (販売価格) as it's comparable to resale market
                price_el = sell_price_el or buy_price_el
                if not price_el:
                    continue

                price = self._parse_price(price_el.get_text(strip=True))
                url = ""
                if link_el:
                    href = link_el.get("href", "")
                    url = f"{self.BASE_URL}{href}" if href.startswith("/") else href

                # Determine if this is buy price or sell price
                price_type = "sell" if sell_price_el else "buy"

                if price > 0:
                    items.append(ScrapedItem(
                        product_name=title,
                        brand=brand,
                        model=model,
                        price=price,
                        listing_url=url,
                        source=self.SOURCE_NAME,
                        item_type=item_type,
                        raw_data={"title": title, "price_type": price_type},
                    ))

                # Also capture buy price separately if both exist
                if sell_price_el and buy_price_el:
                    buy_price = self._parse_price(buy_price_el.get_text(strip=True))
                    if buy_price > 0:
                        items.append(ScrapedItem(
                            product_name=title,
                            brand=brand,
                            model=model,
                            price=buy_price,
                            listing_url=url,
                            source=f"{self.SOURCE_NAME}_buy",
                            item_type=item_type,
                            raw_data={"title": title, "price_type": "buy"},
                        ))

            except Exception as e:
                logger.warning(f"Error parsing Daikokuya listing: {e}")

        logger.info(f"Daikokuya: found {len(items)} items for '{query}'")
        return items

    def _parse_price(self, price_text: str) -> int:
        cleaned = re.sub(r"[¥,\s円税込（税込）]", "", price_text)
        try:
            return int(cleaned)
        except ValueError:
            return 0
