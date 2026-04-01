from playwright.async_api import async_playwright
from servicies.infomoney import *


MARKET_DATA = {}


async def scrape_infomoney_dom(page):
    """Extrai Nome e Valor do InfoMoney via JavaScript."""

    try:
        # Extração focada nas classes específicas que você forneceu
        data = await page.evaluate('''() => {
            // 1. Busca o nome "Bitcoin" (o h2 dentro da div de títulos)
            const nameEl = document.querySelector('h2.im-mob-core-heading-3');

            // 2. Busca o preço "353.460,00" (o h2 com heading-1 na área de valor)
            // Usamos uma combinação de classes para não confundir com o h1 do ticker
            const priceEl = document.querySelector('.items-center.h-8 h2.im-mob-core-heading-1');

            if (!nameEl || !priceEl) return null;

            return {
                name: nameEl.innerText.trim(),
                price: priceEl.innerText.trim()
            };
        }''')

        if data:



            MARKET_DATA[data['name']] = {
                "price": data['price']
            }
    except:
        pass


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        asyncio.create_task(display_timer_infomoney(1, MARKET_DATA))

        print("🚀 Acessando InfoMoney Cotações...")
        # URL
        await page.goto("https://www.infomoney.com.br/", wait_until="domcontentloaded")

        last_url = page.url

        while True:
            pages = context.pages
            if len(pages) > 1:
                # Se abriu uma nova, a última da lista é a ativa
                new_page = pages[-1]
                print(f"🔄 Nova aba detectada: {new_page.url}")

                # Fecha a aba antiga para não pesar a memória
                await page.close()

                # Transfere o controle para a nova aba
                page = new_page

                # Espera a nova aba carregar os elementos
                await page.wait_for_load_state("domcontentloaded")

            # --- CAPTURA DE DADOS ---
            # Passamos a 'page' atual (que pode ser a nova aba)
            await scrape_infomoney_dom(page)
            await asyncio.sleep(0.5)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nEncerrado.")