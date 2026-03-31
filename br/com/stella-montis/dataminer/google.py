import asyncio

from playwright.async_api import async_playwright

from servicies.google_finance_service import *

# Dicionário Global Único
MARKET_DATA = {}


async def scrape_google_finance_dom(page):

    try:
        # 1. Ativo
        # Usamos o seletor de acessibilidade, que o Google raramente muda.
        name_locator = page.locator('[role="heading"][aria-level="1"][class="zzDege"]').first
        name = await name_locator.inner_text() if await name_locator.count() > 0 else "Google Asset"

        # 2. Preço
        # O Google guarda o valor REAL no atributo 'data-last-price'.
        # Isso evita problemas com formatação de moeda (R$, $, etc).
        price_container = page.locator('[data-last-price]').first

        if await price_container.count() > 0:
            # Pegamos o valor bruto do atributo de dados
            raw_price = await price_container.get_attribute("data-last-price")

            # Pega a moeda também do atributo de dados e caso não exista tenta no outro atributo
            currency = await price_container.get_attribute("data-currency-code")
            if currency is None:
                currency = await price_container.get_attribute("data-exchange")

            # Atualiza o dicionário global
            MARKET_DATA[name.strip()] = {
                "price": raw_price,
                "currency": currency,

            }
    except Exception as e:
        print(f'ERROR EM: {e}')


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="chrome", headless=False)
        page = await browser.new_page()

        asyncio.create_task(display_timer_google_finance(1, MARKET_DATA))

        url = "https://www.google.com/finance"
        print("🚀 Acessando Google Finance...")
        await page.goto(url, wait_until="domcontentloaded")

        last_url = page.url

        while True:
            # 'F5' Automático: Se você mudou a URL, o script recarrega
            # Gambiarra para fazer o DOM atualizar 'automaticamente' o código detecta se houve alguma mudança na URL e faz a mudança
            if page.url != last_url:
                await page.reload(wait_until="domcontentloaded")
                last_url = page.url

            await scrape_google_finance_dom(page)
            await asyncio.sleep(0.5)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nEncerrado.")
