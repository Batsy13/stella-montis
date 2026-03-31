import asyncio
from datetime import datetime

from playwright.async_api import async_playwright

from servicies.tradingview_service import *

# Estado global dos dados
MAKET_DATA = {}


async def scrape_dom_elements(page):

    try:
        # 1. Captura o Nome Ativo
        # Se o h1 sumir em algumas abas, buscamos no header principal
        name_element = page.locator('h1[class*="title-"], h2[class*="title-"]').first

        if name_element is "Indices":
            name_element = ""

        name = await name_element.inner_text()

        # Busca por classes de sistema (js-) que o TradingView usa para o Data-Binding.
        # Essas classes são MUITO mais estáveis que classes aleatórias
        price_locator = page.locator('.js-symbol-last').first
        currency_locator = page.locator('.js-symbol-currency').first

        # Verifica se os elementos estão visíveis antes de extrair
        if await price_locator.is_visible():
            # .text_content() captura o número completo (incluindo o span dos centavos)
            raw_price = await price_locator.text_content()
            clean_price = raw_price.strip() if raw_price else "N/A"

            currency = await currency_locator.inner_text() if await currency_locator.count() > 0 else "USD"

            # Atualiza o dicionário global
            MAKET_DATA[name.strip()] = {
                "price": clean_price,
                "currency": currency.strip(),
                "last_update": datetime.now().strftime('%H:%M:%S')
            }
    except Exception as e:
        print(f"ERRO EM: {e}")

async def main():
    async with async_playwright() as p:
        # Abrimos o Chrome visível para você acompanhar
        browser = await p.chromium.launch(channel="chrome", headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # Inicia o temporizador visual
        asyncio.create_task(display_timer_tradingview(3, MAKET_DATA))

        url = "https://www.tradingview.com/symbols/"
        print(f"🚀 Acessando {url}...")
        await page.goto(url, wait_until="domcontentloaded")

        # Loop de captura dinâmica do DOM
        while True:
            # Esta função "lê" a tela a cada ciclo
            await scrape_dom_elements(page)

            # Atualiza os valores da moeda a cada 'x' segundos
            await asyncio.sleep(0.5)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nEncerrado.")
