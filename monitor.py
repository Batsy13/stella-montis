import asyncio
from datetime import datetime
from playwright.async_api import async_playwright
from loguru import logger

async def monitor_price(url: str, selector: str, interval: int = 10):
    
    logger.info(f"Starting monitoring | URL: {url} | Selector: {selector}")

    if not url.startswith("http"):
        logger.error("Invalid URL provided")
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
                            logger.info(f"Selector used: {selector}")
                            logger.info(f"Initial value: {current_value}")
                        elif current_value != last_value:
                            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            logger.warning(f"[{now}] Value changed | Old: {last_value} | New: {current_value}")
                            last_value = current_value
                
                await asyncio.sleep(interval)
        except Exception as e:
            logger.error(f"Monitoring error: {str(e)}")