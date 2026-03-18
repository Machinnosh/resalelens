"""Yahoo Auction (ヤフオク) scraper for ResaleLens."""

import logging
import re
from datetime import datetime
from typing import Optional

from bs4 import BeautifulSoup

from .base import BaseScraper, ScrapedItem

logger = logging.getLogger(__name__)


class YahooAuctionScraper(BaseScraper):
    """Scrape completed auctions from Yahoo Auctions Japan."""

    SOURCE_NAME = "yahoo_auction"
    BASE_URL = "https://auctions.yahoo.co.jp"
    MIN_DELAY = 2.0
    MAX_DELAY = 4.0

    async def scrape_brand(self, brand: str, model: str, item_type: str = "bag") -> list[ScrapedItem]:
        """Scrape Yahoo Auction completed listings."""
        items = []
        query = f"{brand} {model}"

        # Yahoo Auctions completed items search (updated URL structure)
        search_url = f"{self.BASE_URL}/search/search"
        params = {
            "p": query,
            "va": query,
            "is_postage_mode": "1",
            "dest_pref_code": "13",
            "exflg": "1",
            "b": "1",
            "n": "50",
            "select": "sold",
        }

        response = await self._fetch(search_url, params=params)
        if not response:
            return items

        soup = BeautifulSoup(response.text, "html.parser")

        # Parse auction results
        for listing in soup.select(".Product"):
            try:
                title_el = listing.select_one(".Product__titleLink")
                price_el = listing.select_one(".Product__priceValue")
                date_el = listing.select_one(".Product__time")

                if not title_el or not price_el:
                    continue

                title = title_el.get_text(strip=True)
                price = self._parse_price(price_el.get_text(strip=True))
                url = title_el.get("href", "")
                sold_date = self._parse_date(date_el.get_text(strip=True)) if date_el else None

                if price > 0:
                    items.append(ScrapedItem(
                        product_name=title,
                        brand=brand,
                        model=model,
                        price=price,
                        sold_date=sold_date,
                        listing_url=url,
                        source=self.SOURCE_NAME,
                        item_type=item_type,
                        raw_data={"title": title},
                    ))
            except Exception as e:
                logger.warning(f"Error parsing Yahoo listing: {e}")
                continue

        logger.info(f"Yahoo Auction: found {len(items)} items for '{query}'")
        return items

    def _get_category(self, item_type: str) -> str:
        categories = {
            "bag": "2084053669",  # ブランド別 > バッグ
            "wallet": "2084053675",  # 財布
            "watch": "2084053672",  # 腕時計
        }
        return categories.get(item_type, "")

    def _parse_price(self, price_text: str) -> int:
        cleaned = re.sub(r'[¥,\s円]', '', price_text)
        try:
            return int(cleaned)
        except ValueError:
            return 0

    def _parse_date(self, date_text: str) -> Optional[datetime]:
        try:
            # Yahoo format: "3月15日 21:30"
            match = re.search(r'(\d+)月(\d+)日', date_text)
            if match:
                month, day = int(match.group(1)), int(match.group(2))
                year = datetime.now().year
                return datetime(year, month, day)
        except (ValueError, TypeError):
            pass
        return None
