# monitor_service.py

**Caminho:** `app/services/monitor_service.py`  
**Responsabilidade:** Loop assíncrono de polling que monitora um elemento da página e, ao detectar mudança, notifica via Google Forms — tanto por HTTP quanto abrindo o formulário visualmente no browser.

---

## Código Completo

```python
import asyncio
import requests
from datetime import datetime
from playwright.async_api import async_playwright
from loguru import logger

GOOGLE_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLScYm5JlmnR1F2THqf00mKa3C71hgAVa2HLbIg84-88rw74ySw/formResponse"
GOOGLE_FORM_VIEW = "https://docs.google.com/forms/d/e/1FAIpQLScYm5JlmnR1F2THqf00mKa3C71hgAVa2HLbIg84-88rw74ySw/viewform"
FORM_ENTRY = "entry.1608177186"

def send_google_form(message):
    try:
        requests.post(GOOGLE_FORM_URL, data={FORM_ENTRY: message})
    except Exception as e:
        logger.error(f"Erro ao enviar formulário: {e}")

async def show_visual_form(message):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            await page.goto(GOOGLE_FORM_VIEW)
            await page.wait_for_selector('textarea')
            await page.fill('textarea', message)
            await page.locator('text=Enviar').click()
            await page.wait_for_timeout(3000)
            await browser.close()
    except Exception as e:
        logger.error(f"Erro no formulário visual: {e}")

async def monitor_price(url: str, selector: str, interval: int = 10):
    logger.info(f"Starting persistent monitoring | URL: {url}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        last_value = None

        try:
            await page.goto(url, wait_until="load", timeout=30000)

            while True:
                try:
                    locator = page.locator(selector).first
                    if await locator.is_visible():
                        current_value = (await locator.inner_text()).strip()
                        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                        if current_value:
                            if last_value is None:
                                last_value = current_value
                                logger.info(f"Initial value: {current_value}")
                                start_msg = (
                                    f"Monitoramento Iniciado\n\n"
                                    f"URL: {url}\n"
                                    f"Valor inicial: {current_value}\n"
                                    f"Data: {now}"
                                )
                                asyncio.create_task(show_visual_form(start_msg))

                            elif current_value != last_value:
                                logger.info(f"[{now}] Value changed | Old: {last_value} | New: {current_value}")
                                message = (
                                    f"Valor alterado!\n\n"
                                    f"URL: {url}\nData: {now}\n\n"
                                    f"Valor antigo: {last_value}\n"
                                    f"Novo valor: {current_value}"
                                )
                                asyncio.create_task(show_visual_form(message))
                                last_value = current_value

                    await asyncio.sleep(interval)

                except Exception as e:
                    if "closed" in str(e).lower():
                        logger.info("Playwright connection closed. Finishing task.")
                        break
                    raise e

        except asyncio.CancelledError:
            logger.info(f"Monitoring task for {url} was cancelled by user/system.")
        except Exception as e:
            logger.error(f"Unexpected monitoring error: {e}")
        finally:
            end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            end_msg = (
                f"Monitoramento Finalizado\n\n"
                f"O monitoramento para a URL {url} foi encerrado às {end_time}."
            )
            try:
                await show_visual_form(end_msg)
            except Exception as e:
                logger.error(f"Could not send termination form: {e}")
            try:
                if not browser.is_connected():
                    logger.info("Browser already disconnected.")
                else:
                    await browser.close()
            except:
                pass
            logger.info(f"Resource cleanup finished for {url}")
```

---

## Funções

### `send_google_form(message)`

Envia o formulário via **HTTP POST** direto ao endpoint de resposta do Google Forms. Operação silenciosa e rápida.

```python
def send_google_form(message):
    requests.post(GOOGLE_FORM_URL, data={"entry.1608177186": message})
```

| Parâmetro | Tipo | Descrição |
|---|---|---|
| `message` | `str` | Texto a ser inserido no campo do formulário |

---

### `show_visual_form(message)`

Abre o Google Forms visualmente no Chromium, preenche o campo `textarea` com a mensagem e clica no botão "Enviar". Demonstra a interação com uma página pública que o sistema não controla.

```python
async def show_visual_form(message):
    browser = await p.chromium.launch(headless=False)
    page = await browser.new_page()
    await page.goto(GOOGLE_FORM_VIEW)
    await page.wait_for_selector('textarea')
    await page.fill('textarea', message)
    await page.locator('text=Enviar').click()
```

---

### `monitor_price(url, selector, interval=10)`

Loop principal de monitoramento.

| Parâmetro | Tipo | Padrão | Descrição |
|---|---|---|---|
| `url` | `str` | — | URL da página a monitorar |
| `selector` | `str` | — | CSS selector do elemento |
| `interval` | `int` | `10` | Intervalo em segundos entre verificações |

---

## Mensagens Enviadas ao Google Forms

### Monitoramento Iniciado

```
Monitoramento Iniciado

URL: https://site.com
Valor inicial: $74,228.31
Data: 2026-04-15 10:00:00
```

### Valor Alterado

```
Valor alterado!

URL: https://site.com
Data: 2026-04-15 10:05:32

Valor antigo: $74,228.31
Novo valor: $74,231.83
```

### Monitoramento Finalizado

```
Monitoramento Finalizado

O monitoramento para a URL https://site.com foi encerrado às 2026-04-15 10:30:00.
```

---

## Ciclo de Vida

```
monitor_price() iniciada
        │
        ├─ Abre Chromium headless=False
        ├─ page.goto(url)
        │
        └─ Loop (interval=10s):
               │
               ├─ locator.is_visible()?
               │    └─ inner_text() → current_value
               │
               ├─ last_value is None → salva inicial + show_visual_form("Iniciado")
               ├─ igual → sleep()
               └─ diferente → logger.info() + show_visual_form("Alterado")
                                   atualiza last_value
               │
               ├─ "closed" → break (browser fechado pelo usuário)
               ├─ CancelledError → encerra (via /stop)
               └─ finally → show_visual_form("Finalizado") + browser.close()
```

---

## Tratamento de Erros

| Situação | Comportamento |
|---|---|
| Browser fechado pelo usuário | `"closed" in str(e)` → `break` gracioso |
| `/stop` chamado | `CancelledError` → `finally` executa encerramento |
| Falha no Google Forms | `logger.error()`, execução continua |
| Erro inesperado no loop | `raise e` (re-lança para o handler externo) |
