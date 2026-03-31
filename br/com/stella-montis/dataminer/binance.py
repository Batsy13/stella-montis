import asyncio

from playwright.async_api import async_playwright

from servicies.binance_service import *

# Estado global dos dados
MARKET_DATA = {}


async def scrape_binance_dom(page):
    """Extrai Ativo, Rótulo e Preço da estrutura da Binance."""
    try:
        # 1. Capturar o h1
        # Usando uma hierarquia segura para chegar no h1 do topo 'Ativo'
        symbol = await page.inner_text('div.text-PrimaryText h1')

        # 2. Capturar o 'Rótulo'
        # O seletor busca o link dentro da área de descrição
        label = await page.inner_text('a.text-TextLink')

        # 3. Capturar o 'Preço'
        # Usamos a classe 'showPrice' que é o padrão da Binance para o preço principal
        price = await page.inner_text('.showPrice')

        # Atualiza o dicionário global usando o símbolo como chave
        MARKET_DATA[symbol] = {
            "symbol": symbol.strip(),
            "label": label.strip(),
            "price": price.strip()
        }
    except Exception as e:
        print(f'ERRO EM: {e}')


async def main():
    async with async_playwright() as p:
        # Lança o Chrome com perfil de usuário para evitar bloqueios básicos
        browser = await p.chromium.launch(channel="chrome", headless=False)
        page = await browser.new_page()

        # Inicia o Dashboard no terminal
        asyncio.create_task(display_timer_binance(2, MARKET_DATA))

        # URL da Binance
        url = "https://www.binance.com/pt-BR/trade"
        print(f"🚀 Conectando à Binance...")
        await page.goto(url, wait_until="domcontentloaded")

        # Loop de captura
        while True:
            await scrape_binance_dom(page)
            # Frequência de leitura do DOM
            await asyncio.sleep(2)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Sistema encerrado.")
