from playwright.async_api import async_playwright
from servicies.investidor10 import *

MARKET_DATA = {}

async def scrape_investidor10_dom(page):
    try:
        # 1. Captura o Ativo
        # O h1 dentro da div name-ticker é o alvo mais direto
        name_locator = page.locator('.name-ticker h1').first
        name = await name_locator.inner_text()

        # 2. Captura a Cotação (Moeda e Valor)
        quotation_locator = page.locator('.stockCurrentQuotation .value, ._card-body .value').first
        raw_quotation = await quotation_locator.inner_text()

        if name and raw_quotation:
            # Limpamos o texto para separar Moeda de Valor
            # Exemplo: "US$ 174,40" -> ["US$", "174,40"]
            parts = raw_quotation.replace('\xa0', ' ').strip().split(' ')
            currency = parts[0] if len(parts) > 1 else "BRL"
            price = parts[-1]

            ticker = name.strip()

            MARKET_DATA[ticker] = {
                "price": price,
                "currency": currency,
            }
    except Exception as e:
        print(f"ERRO EM : {e}")

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # Dashboard focado no Investidor10
        asyncio.create_task(display_timer_investidor10(1, MARKET_DATA))

        print("🚀 Acessando Investidor10...")

        url = "https://investidor10.com.br/"
        await page.goto(url, wait_until="domcontentloaded")

        while True:

            await scrape_investidor10_dom(page)
            await asyncio.sleep(0.5)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Encerrado.")