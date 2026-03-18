"""Take iPhone-style app screenshots for App Store / Google Play submission."""

import asyncio
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from playwright.async_api import async_playwright

BASE_URL = "http://localhost:8099"
OUTPUT_DIR = "store-assets/screenshots"

# iPhone 15 Pro Max: 1290x2796 physical pixels
# Logical: 430x932 at 3x scale
IPHONE_CONFIG = {
    "viewport": {"width": 428, "height": 926},
    "device_scale_factor": 3,  # 428*3=1284, 926*3=2778
    "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "is_mobile": True,
    "has_touch": True,
}

SCREENS = [
    {
        "name": "01_search_home",
        "url": f"{BASE_URL}/",
        "wait": 4,
    },
    {
        "name": "02_brand_hermes",
        "url": f"{BASE_URL}/brand/hermes",
        "wait": 3,
    },
    {
        "name": "03_result_birkin",
        "url": f"{BASE_URL}/result/hermes-birkin",
        "wait": 4,
    },
    {
        "name": "04_ranking",
        "url": f"{BASE_URL}/ranking",
        "wait": 3,
    },
    {
        "name": "05_profile",
        "url": f"{BASE_URL}/profile",
        "wait": 2,
    },
]


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # iOS subfolder
        ios_dir = f"{OUTPUT_DIR}/ios"
        import os
        os.makedirs(ios_dir, exist_ok=True)

        context = await browser.new_context(
            viewport=IPHONE_CONFIG["viewport"],
            device_scale_factor=IPHONE_CONFIG["device_scale_factor"],
            user_agent=IPHONE_CONFIG["user_agent"],
            is_mobile=IPHONE_CONFIG["is_mobile"],
            has_touch=IPHONE_CONFIG["has_touch"],
            locale="ja-JP",
            color_scheme="light",
        )
        page = await context.new_page()

        # Hide web-only elements (browser scrollbar, etc.)
        await page.add_style_tag(content="""
            ::-webkit-scrollbar { display: none !important; }
            body { -webkit-font-smoothing: antialiased; }
        """)

        for screen in SCREENS:
            print(f"Capturing: {screen['name']}...")
            try:
                await page.goto(screen["url"], wait_until="networkidle", timeout=15000)
            except Exception:
                await page.goto(screen["url"], timeout=15000)
            await asyncio.sleep(screen["wait"])

            # Dismiss any error toasts/banners
            try:
                await page.evaluate("""
                    document.querySelectorAll('[class*="error"], [class*="toast"], [class*="banner"]')
                        .forEach(el => el.style.display = 'none');
                """)
            except Exception:
                pass

            path = f"{ios_dir}/{screen['name']}.png"
            await page.screenshot(path=path, full_page=False)
            print(f"  Saved: {path} (1290x2796)")

        # Also take Android screenshots (same content, different folder)
        android_dir = f"{OUTPUT_DIR}/android"
        os.makedirs(android_dir, exist_ok=True)

        # Pixel 7 Pro: 1440x3120 at 3.5x scale -> 412x891 logical
        await context.close()
        context = await browser.new_context(
            viewport={"width": 412, "height": 891},
            device_scale_factor=3.5,
            user_agent="Mozilla/5.0 (Linux; Android 14; Pixel 7 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            is_mobile=True,
            has_touch=True,
            locale="ja-JP",
            color_scheme="light",
        )
        page = await context.new_page()
        await page.add_style_tag(content="::-webkit-scrollbar { display: none !important; }")

        for screen in SCREENS:
            print(f"Android: {screen['name']}...")
            try:
                await page.goto(screen["url"], wait_until="networkidle", timeout=15000)
            except Exception:
                await page.goto(screen["url"], timeout=15000)
            await asyncio.sleep(screen["wait"])

            try:
                await page.evaluate("""
                    document.querySelectorAll('[class*="error"], [class*="toast"], [class*="banner"]')
                        .forEach(el => el.style.display = 'none');
                """)
            except Exception:
                pass

            path = f"{android_dir}/{screen['name']}.png"
            await page.screenshot(path=path, full_page=False)
            print(f"  Saved: {path}")

        await browser.close()
        print(f"\nDone! Screenshots saved to {OUTPUT_DIR}/ios/ and {OUTPUT_DIR}/android/")


if __name__ == "__main__":
    asyncio.run(main())
