# monitor_service.py

**Caminho:** `app/services/monitor_service.py`  
**Responsabilidade:** Contém o loop assíncrono de polling que monitora um elemento da página e detecta mudanças de valor.

---

## Código Completo

```python
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright, Error as PlaywrightError
from loguru import logger
from services.email_service import send_email

async def monitor_price(url: str, selector: str, email: str, interval: int = 10):
    logger.info(f"Starting persistent monitoring | URL: {url}")

    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    start_subject = "Monitoramento Iniciado"
    start_message = f"O monitoramento para a URL {url} foi iniciado com sucesso às {start_time}."
    asyncio.create_task(asyncio.to_thread(send_email, email, start_subject, start_message))

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

                        if current_value:
                            if last_value is None:
                                last_value = current_value
                                logger.info(f"Initial value: {current_value}")

                            elif current_value != last_value:
                                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                log_msg = f"[{now}] Value changed | Old: {last_value} | New: {current_value}"
                                logger.warning(log_msg)

                                subject = "Valor alterado!"
                                message = (
                                    f"O valor monitorado foi alterado.\n\n"
                                    f"URL: {url}\n"
                                    f"Data: {now}\n\n"
                                    f"Valor antigo: {last_value}\n"
                                    f"Novo valor: {current_value}"
                                )
                                asyncio.create_task(
                                    asyncio.to_thread(send_email, email, subject, message)
                                )
                                last_value = current_value

                    await asyncio.sleep(interval)

                except PlaywrightError as e:
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
            end_subject = "Monitoramento Finalizado"
            end_message = f"O monitoramento para a URL {url} foi encerrado às {end_time}."
            try:
                await asyncio.to_thread(send_email, email, end_subject, end_message)
            except Exception as e:
                logger.error(f"Could not send termination email: {e}")
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

## Função `monitor_price`

### Assinatura

```python
async def monitor_price(url: str, selector: str, email: str, interval: int = 10)
```

### Parâmetros

| Parâmetro | Tipo | Padrão | Descrição |
|---|---|---|---|
| `url` | `str` | — | URL da página a monitorar |
| `selector` | `str` | — | CSS selector do elemento alvo |
| `email` | `str` | — | E-mail de destino para notificações |
| `interval` | `int` | `10` | Intervalo em segundos entre cada verificação |

---

## Ciclo de Vida do Monitoramento

```
monitor_price() chamada
        │
        ├─ E-mail "Monitoramento Iniciado" (assíncrono)
        │
        ├─ Abre Chromium headless
        ├─ Navega para url (timeout 30s)
        │
        └─ Loop infinito:
               │
               ├─ locator = page.locator(selector).first
               ├─ is_visible()? Sim ──────────────────────────────┐
               │                                                   │
               │   Não → sleep(interval)                          │
               │                                                   ▼
               │                              current_value = inner_text().strip()
               │                                        │
               │                         last_value is None?
               │                          Sim → salva inicial, log INFO
               │                          Não → compara com last_value
               │                                   │
               │                         Igual → sleep(interval)
               │                         Diferente → log WARNING + e-mail
               │                                      atualiza last_value
               │
               ├─ PlaywrightError("closed") → break
               ├─ CancelledError → encerra
               └─ Exception → log ERROR, encerra
                       │
                       └─ finally: e-mail "Monitoramento Finalizado"
                                   browser.close()
```

---

## Tratamento de Erros

### `PlaywrightError` com "closed"

Ocorre quando o usuário fecha o browser headless manualmente. O loop encerra graciosamente sem lançar exceção.

```python
except PlaywrightError as e:
    if "closed" in str(e).lower():
        logger.info("Playwright connection closed. Finishing task.")
        break
    raise e  # re-lança erros desconhecidos
```

### `asyncio.CancelledError`

Ocorre quando a task é cancelada pelo sistema (ex.: desligamento do servidor).

### `Exception` genérica

Captura qualquer erro inesperado (timeout de rede, elemento removido do DOM, etc.) e loga com nível ERROR.

### Bloco `finally`

**Sempre** executado ao final, independente do motivo de encerramento:
- Envia e-mail de notificação de encerramento
- Fecha o browser de forma segura

---

## Envio Assíncrono de E-mail

O `send_email` é uma função síncrona (usa `smtplib`). Para não bloquear o event loop assíncrono, é executada em uma thread separada:

```python
asyncio.create_task(
    asyncio.to_thread(send_email, email, subject, message)
)
```

Isso garante que o loop de monitoramento **não trava** durante o envio do e-mail.

---

## Exemplo de Log Gerado

```
2026-04-14 23:38:30 | INFO     | Starting persistent monitoring | URL: https://coinmarketcap.com/...
2026-04-14 23:38:40 | INFO     | Initial value: $74,228.31
2026-04-14 23:38:51 | WARNING  | [2026-04-14 23:38:51] Value changed | Old: $74,228.31 | New: $74,228.08
2026-04-14 23:39:01 | WARNING  | [2026-04-14 23:39:01] Value changed | Old: $74,228.08 | New: $74,228.83
```
