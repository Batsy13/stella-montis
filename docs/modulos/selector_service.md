# selector_service.py

**Caminho:** `app/services/selector_service.py`  
**Responsabilidade:** Abre um browser Chromium real na URL informada, injeta scripts de seleção visual e retorna o CSS selector do elemento clicado via WebSocket.

---

## Código Completo

```python
import asyncio
from playwright.async_api import async_playwright
from loguru import logger
from fastapi import WebSocket

async def open_live_selector(url: str, websocket: WebSocket):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/123.0.0.0"
        )
        page = await context.new_page()

        async def on_xpath_selected(xpath: str):
            logger.success(f"XPath: {xpath}")
            await websocket.send_json({"type": "xpath_result", "xpath": xpath})

        await page.expose_function("sendToPython", on_xpath_selected)

        await page.add_init_script("""
            let currentSelectedElement = null;

            const injectCSS = setInterval(() => {
                if (document.head) {
                    const style = document.createElement('style');
                    style.innerHTML = `
                        .scraper-hover   { outline: 2px solid red !important; cursor: crosshair !important; }
                        .scraper-selected{ outline: 3px solid blue !important; background-color: rgba(0,0,255,0.1) !important; }
                    `;
                    document.head.appendChild(style);
                    clearInterval(injectCSS);
                }
            }, 50);

            document.addEventListener('mouseover', (e) => { e.target.classList.add('scraper-hover'); }, true);
            document.addEventListener('mouseout',  (e) => { e.target.classList.remove('scraper-hover'); }, true);

            document.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();

                if (currentSelectedElement) {
                    currentSelectedElement.classList.remove('scraper-selected');
                }
                currentSelectedElement = e.target;
                currentSelectedElement.classList.add('scraper-selected');

                let el = e.target;
                let path = [];
                while (el.nodeType === Node.ELEMENT_NODE) {
                    let selector = el.nodeName.toLowerCase();
                    if (el.id) {
                        path.unshift('#' + el.id);
                        break;
                    } else {
                        let sib = el, nth = 1;
                        while (sib = sib.previousElementSibling) {
                            if (sib.nodeName.toLowerCase() === selector) nth++;
                        }
                        selector += `:nth-of-type(${nth})`;
                    }
                    path.unshift(selector);
                    el = el.parentNode;
                }

                window.sendToPython(path.join(' > '));
            }, true);
        """)

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            while browser.is_connected():
                await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"Erro no Live Selector: {e}")
            await websocket.send_json({"type": "error", "message": str(e)})
```

---

## Função `open_live_selector`

### Assinatura

```python
async def open_live_selector(url: str, websocket: WebSocket)
```

### Parâmetros

| Parâmetro | Tipo | Descrição |
|---|---|---|
| `url` | `str` | URL da página que o usuário quer inspecionar |
| `websocket` | `WebSocket` | Conexão WebSocket para enviar o resultado ao frontend |

---

## Como Funciona

### 1. Abertura do Browser

```python
browser = await p.chromium.launch(headless=False)
```

O browser abre **visível** para o usuário. Nenhum HTML é modificado — a página carrega exatamente como no navegador comum, incluindo fontes externas, CDNs e estilos.

### 2. `page.expose_function`

```python
await page.expose_function("sendToPython", on_xpath_selected)
```

Cria uma ponte entre o JavaScript da página e o Python. Quando o JavaScript chama `window.sendToPython(xpath)`, o callback `on_xpath_selected` é executado no lado Python com o valor recebido.

### 3. `page.add_init_script`

```python
await page.add_init_script("...")
```

Injeta o script **antes** de qualquer outro script da página. Isso garante que os event listeners sejam registrados mesmo em SPAs que substituem o DOM dinamicamente.

O script injeta CSS via `setInterval` aguardando o `document.head` estar disponível — necessário para páginas com carregamento tardio.

### 4. Cálculo do CSS Selector

O algoritmo percorre o DOM de baixo para cima:

```javascript
while (el.nodeType === Node.ELEMENT_NODE) {
    if (el.id) {
        path.unshift('#' + el.id);
        break;              // ID é único — para aqui
    } else {
        // conta siblings do mesmo tipo para usar :nth-of-type
        selector += `:nth-of-type(${nth})`;
    }
    path.unshift(selector);
    el = el.parentNode;
}
```

**Exemplos de selectors gerados:**

```
#section-coin-overview > div:nth-of-type(2) > span:nth-of-type(1)
table:nth-of-type(1) > tbody:nth-of-type(1) > tr:nth-of-type(2) > td:nth-of-type(3)
```

### 5. Retorno via WebSocket

```python
async def on_xpath_selected(xpath: str):
    await websocket.send_json({"type": "xpath_result", "xpath": xpath})
```

O resultado é enviado ao frontend imediatamente após o clique, preenchendo o campo **Vetor de Dados** da interface.

### 6. Manutenção da Conexão

```python
while browser.is_connected():
    await asyncio.sleep(1)
```

A função fica ativa enquanto o browser estiver aberto, permitindo múltiplos cliques e re-seleções. Encerra quando o usuário fecha o browser.

---

## Diferença em Relação à Abordagem Anterior (Proxy Iframe)

| Aspecto | Proxy Iframe (removido) | Live Selector (atual) |
|---|---|---|
| Renderização | HTML re-servido pelo backend | Browser real, sem modificações |
| Compatibilidade | Quebrava com fontes/estilos externos | Universal — qualquer site |
| Scripts da página | Removidos via regex | Intactos |
| Comunicação | `postMessage` (iframe → pai) | `expose_function` (browser → Python → WebSocket) |
| Segurança | Remoção de CSP/X-Frame-Options | Não altera headers |
