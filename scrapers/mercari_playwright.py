"""Mercari scraper using Playwright for SPA rendering."""

import asyncio
import logging
import re
from datetime import datetime
from typing import Optional

from playwright.async_api import async_playwright, Page, Browser

from .base import BaseScraper, ScrapedItem

logger = logging.getLogger(__name__)


class MercariPlaywrightScraper(BaseScraper):
    """Scrape sold listings from Mercari using Playwright (headless browser)."""

    SOURCE_NAME = "mercari"
    BASE_URL = "https://jp.mercari.com"
    MIN_DELAY = 3.0
    MAX_DELAY = 7.0

    def __init__(self):
        super().__init__()
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None

    async def _init_browser(self):
        """Initialize Playwright browser."""
        pw = await async_playwright().start()
        self.browser = await pw.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"],
        )
        context = await self.browser.new_context(
            user_agent=self.USER_AGENTS[0],
            viewport={"width": 1280, "height": 800},
            locale="ja-JP",
        )
        self.page = await context.new_page()

    async def _close_browser(self):
        if self.browser:
            await self.browser.close()

    async def scrape_brand(self, brand: str, model: str, item_type: str = "bag") -> list[ScrapedItem]:
        """Scrape Mercari sold listings using Playwright."""
        items = []
        query = f"{brand} {model}"

        if not self.browser:
            await self._init_browser()

        try:
            # Navigate to search page with sold items filter
            category_id = self._get_category_id(item_type)
            search_url = (
                f"{self.BASE_URL}/search?keyword={query}"
                f"&status=sold_out&category_id={category_id}"
                f"&sort=created_time&order=desc"
            )

            await self.page.goto(search_url, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(2)  # Wait for dynamic content

            # Scroll to load more items
            for _ in range(3):
                await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(1.5)

            # Extract listing data
            listings = await self.page.query_selector_all('[data-testid="item-cell"]')

            if not listings:
                # Fallback selector
                listings = await self.page.query_selector_all('li[class*="item"]')

            for listing in listings[:50]:  # Limit to 50 items per query
                try:
                    item = await self._parse_listing(listing, brand, model, item_type)
                    if item and item.price > 0:
                        items.append(item)
                except Exception as e:
                    logger.debug(f"Error parsing Mercari listing: {e}")
                    continue

            logger.info(f"Mercari Playwright: found {len(items)} items for '{query}'")

        except Exception as e:
            logger.error(f"Mercari Playwright error for '{query}': {e}")

        await self._delay()
        return items

    async def _parse_listing(self, element, brand: str, model: str, item_type: str) -> Optional[ScrapedItem]:
        """Parse a single Mercari listing element."""
        # Try to extract title
        title_el = await element.query_selector('[class*="itemName"], [class*="name"], h3, p')
        if not title_el:
            return None
        title = await title_el.inner_text()

        # Extract price
        price_el = await element.query_selector('[class*="price"], [class*="Price"]')
        if not price_el:
            return None
        price_text = await price_el.inner_text()
        price = self._parse_price(price_text)

        # Extract link
        link_el = await element.query_selector("a")
        url = ""
        if link_el:
            href = await link_el.get_attribute("href")
            if href:
                url = f"{self.BASE_URL}{href}" if href.startswith("/") else href

        return ScrapedItem(
            product_name=title.strip(),
            brand=brand,
            model=model,
            price=price,
            condition=None,
            sold_date=datetime.now(),
            listing_url=url,
            source=self.SOURCE_NAME,
            item_type=item_type,
            raw_data={"title": title},
        )

    def _get_category_id(self, item_type: str) -> str:
        categories = {
            "bag": "4",
            "wallet": "65",
            "watch": "107",
        }
        return categories.get(item_type, "4")

    def _parse_price(self, price_text: str) -> int:
        cleaned = re.sub(r"[¥,\s円]", "", price_text)
        try:
            return int(cleaned)
        except ValueError:
            return 0

    async def scrape_all(self, queries: list[dict]) -> list[ScrapedItem]:
        """Override to manage browser lifecycle."""
        await self._init_browser()
        try:
            return await super().scrape_all(queries)
        finally:
            await self._close_browser()
