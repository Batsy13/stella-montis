# main.py

**Caminho:** `app/main.py`  
**Responsabilidade:** Ponto de entrada da aplicação. Define os endpoints FastAPI, inicializa o logger e serve a interface web.

---

## Código Completo

```python
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from playwright.async_api import async_playwright
import uvicorn
import re
from services.monitor_service import monitor_price
from pathlib import Path
from core.logger_config import setup_logger
from loguru import logger
import asyncio

if hasattr(asyncio, "WindowsProactorEventLoopPolicy"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent

setup_logger()
logger.info("Application started")

class MonitorRequest(BaseModel):
    url: str
    xpath: str
    email: str
```

---

## Modelo de Dados

### `MonitorRequest`

Modelo Pydantic que valida o corpo da requisição `POST /start`.

| Campo | Tipo | Descrição |
|---|---|---|
| `url` | `str` | URL da página a ser monitorada |
| `xpath` | `str` | CSS selector do elemento alvo (gerado pelo proxy) |
| `email` | `str` | Endereço de e-mail para notificações |

---

## Endpoints

### `GET /`

Serve a interface web principal (`index.html`).

```python
@app.get("/", response_class=HTMLResponse)
async def index():
    template_path = BASE_DIR / "templates" / "index.html"
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()
```

**Resposta:** HTML da interface do usuário.

---

### `POST /start`

Inicia o monitoramento de um elemento em background.

```python
@app.post("/start")
async def start_monitoring(req: MonitorRequest, background_tasks: BackgroundTasks):
    logger.info(f"Monitoring requested | URL: {req.url} | Selector: {req.xpath}")
    background_tasks.add_task(monitor_price, req.url, req.xpath, req.email)
    return {"message": "Monitoring started"}
```

**Body esperado:**
```json
{
  "url": "https://site.com/produto",
  "xpath": "#preco > span:nth-of-type(1)",
  "email": "usuario@gmail.com"
}
```

**Resposta:**
```json
{ "message": "Monitoring started" }
```

!!! info "BackgroundTasks"
    O FastAPI retorna a resposta imediatamente e executa `monitor_price()` em uma tarefa de background assíncrona. O servidor permanece disponível para novas requisições.

---

### `GET /proxy`

Carrega uma URL externa via Playwright, remove restrições de segurança e injeta scripts de seleção visual.

```python
@app.get("/proxy", response_class=HTMLResponse)
async def proxy(url: str):
    ...
```

**Query parameter:** `url` — URL da página a carregar.

**O que o proxy faz internamente:**

1. Abre o Chromium headless com User-Agent customizado
2. Navega para a URL com timeout de 60 segundos
3. Aguarda 5 segundos para JavaScript renderizar
4. Extrai o HTML completo com `page.content()`
5. Remove headers de segurança via regex:
   - `<meta http-equiv="Content-Security-Policy">`
   - `<meta http-equiv="X-Frame-Options">`
   - Todas as tags `<script>` (evita conflitos com scripts injetados)
6. Injeta `<base href="url">` para resolver caminhos relativos
7. Injeta CSS + JS de seleção visual antes de `</body>`

**Scripts injetados no proxy:**

```css
.scraper-hover    { outline: 2px solid red !important; }
.scraper-selected { outline: 3px solid blue !important; }
```

```javascript
// mouseover → destaca em vermelho
// click → destaca em azul e calcula CSS selector
// CSS selector enviado via postMessage para o frame pai
window.parent.postMessage({ xpath: finalSelector }, '*');
```

---

## Configuração do Event Loop (Windows)

```python
if hasattr(asyncio, "WindowsProactorEventLoopPolicy"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
```

!!! note "Por que isso é necessário?"
    No Windows, o event loop padrão (`SelectorEventLoop`) não suporta subprocessos. O Playwright precisa de `ProactorEventLoop` para funcionar corretamente. Esta linha é ignorada em Linux/macOS.

---

## Inicialização

```python
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

O servidor fica disponível em todas as interfaces de rede na porta **8000**.
