from playwright.async_api import async_playwright
from servicies.statusinvest import *

MARKET_DATA = {}

async def scrape_status_invest(page):
    """Extrai os dados do Status Invest usando os seletores de H1 e Strong."""
    try:
        # 1. Captura o Nome do Ativo (H1 com classe lh-4 ou a classe simples h1)
        name_locator = page.locator('h1.lh-4, div.flex-nowrap h1').first
        name = await name_locator.inner_text()

        # 2. Captura o Valor (Strong com classe value dentro da div de valor atual)
        price_locator = page.locator('strong.value').first
        price = await price_locator.inner_text()

        MARKET_DATA[name] = {
            "price": price.strip(),
            "ref": "BRL"
        }
    except Exception as e:
        print(f"ERRO EM: {e}")


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        asyncio.create_task(display_timer_status_invest(1, MARKET_DATA))

        print("🚀 Acessando Status Invest...")
        url = "https://statusinvest.com.br/acoes"
        await page.goto(url, wait_until="domcontentloaded")

        while True:
            await scrape_status_invest(page)
            await asyncio.sleep(0.5)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nEncerrado.")