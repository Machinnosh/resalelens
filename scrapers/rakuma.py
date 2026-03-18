"""Rakuma (ラクマ) scraper for ResaleLens."""

import asyncio
import logging
import re
from datetime import datetime
from typing import Optional

from playwright.async_api import async_playwright, Browser, Page

from .base import BaseScraper, ScrapedItem

logger = logging.getLogger(__name__)


class RakumaScraper(BaseScraper):
    """Scrape sold listings from Rakuma using Playwright (SPA)."""

    SOURCE_NAME = "rakuma"
    BASE_URL = "https://fril.jp"
    MIN_DELAY = 3.0
    MAX_DELAY = 6.0

    def __init__(self):
        super().__init__()
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None

    async def _init_browser(self):
        pw = await async_playwright().start()
        self.browser = await pw.chromium.launch(headless=True)
        context = await self.browser.new_context(
            user_agent=self.USER_AGENTS[1],
            viewport={"width": 1280, "height": 800},
            locale="ja-JP",
        )
        self.page = await context.new_page()

    async def _close_browser(self):
        if self.browser:
            await self.browser.close()

    async def scrape_brand(self, brand: str, model: str, item_type: str = "bag") -> list[ScrapedItem]:
        """Scrape Rakuma sold listings."""
        items = []
        query = f"{brand} {model}"

        if not self.browser:
            await self._init_browser()

        try:
            search_url = f"{self.BASE_URL}/search/{query}?transaction=sold_out&sort=created_at&order=desc"
            await self.page.goto(search_url, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(2)

            # Scroll to load
            for _ in range(2):
                await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(1)

            listings = await self.page.query_selector_all(".item-box")

            for listing in listings[:50]:
                try:
                    title_el = await listing.query_selector(".item-box__item-name, .item-name")
                    price_el = await listing.query_selector(".item-box__item-price, .item-price")
                    link_el = await listing.query_selector("a")

                    if not title_el or not price_el:
                        continue

                    title = await title_el.inner_text()
                    price_text = await price_el.inner_text()
                    price = self._parse_price(price_text)

                    url = ""
                    if link_el:
                        href = await link_el.get_attribute("href")
                        if href:
                            url = f"{self.BASE_URL}{href}" if href.startswith("/") else href

                    if price > 0:
                        items.append(ScrapedItem(
                            product_name=title.strip(),
                            brand=brand,
                            model=model,
                            price=price,
                            sold_date=datetime.now(),
                            listing_url=url,
                            source=self.SOURCE_NAME,
                            item_type=item_type,
                            raw_data={"title": title},
                        ))
                except Exception as e:
                    logger.debug(f"Error parsing Rakuma listing: {e}")

            logger.info(f"Rakuma: found {len(items)} items for '{query}'")

        except Exception as e:
            logger.error(f"Rakuma error for '{query}': {e}")

        await self._delay()
        return items

    def _parse_price(self, price_text: str) -> int:
        cleaned = re.sub(r"[¥,\s円]", "", price_text)
        try:
            return int(cleaned)
        except ValueError:
            return 0

    async def scrape_all(self, queries: list[dict]) -> list[ScrapedItem]:
        await self._init_browser()
        try:
            return await super().scrape_all(queries)
        finally:
            await self._close_browser()
