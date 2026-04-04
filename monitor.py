import asyncio
from datetime import datetime
from playwright.async_api import async_playwright

async def monitor_price(url: str, selector: str, interval: int = 10):
    if not url.startswith("http"):
        return

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        last_value = None
        
        try:
            await page.goto(url, wait_until="load", timeout=30000)
            locator = page.locator(selector).first
            
            while True:
                if await locator.is_visible():
                    current_value = await locator.inner_text()
                    current_value = current_value.strip()
                    
                    if current_value:
                        if last_value is None:
                            last_value = current_value
                            print(f"Position: {selector}")
                            print(f"Initial: {current_value}")
                        elif current_value != last_value:
                            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            print(f"[{now}] Changed! Old: {last_value} | New: {current_value}")
                            last_value = current_value
                
                await asyncio.sleep(interval)
        except Exception as e:
            print(e)