# main.py

**Caminho:** `app/main.py`  
**Responsabilidade:** Ponto de entrada da aplicação. Define os endpoints REST e WebSocket, gerencia o ciclo de vida das tasks de monitoramento e serve a interface web.

---

## Código Completo

```python
import asyncio
from pathlib import Path
from typing import Dict
import sys

import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, BackgroundTasks, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from loguru import logger

from services.monitor_service import monitor_price
from services.selector_service import open_live_selector
from core.logger_config import setup_logger

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"

setup_logger()

class MonitorRequest(BaseModel):
    url: str
    xpath: str

class StopRequest(BaseModel):
    url: str

active_tasks: Dict[str, asyncio.Task] = {}
```

---

## Modelos de Dados

### `MonitorRequest` — usado em `POST /start`

| Campo | Tipo | Descrição |
|---|---|---|
| `url` | `str` | URL da página a ser monitorada |
| `xpath` | `str` | CSS selector do elemento (gerado pelo Live Selector) |
| `username` | `str` | Nome do operador que disparou a tarefa |

### `StopRequest` — usado em `POST /stop`

| Campo | Tipo | Descrição |
|---|---|---|
| `url` | `str` | URL cujo monitoramento deve ser encerrado |
| `username` | `str` | Nome do operador que solicitou a parada |

---

## `active_tasks`

```python
active_tasks: Dict[str, asyncio.Task] = {}
```

Dicionário global que mapeia cada URL monitorada para sua `asyncio.Task`. Permite:
- Verificar se uma URL já está sendo monitorada
- Cancelar uma task específica sem afetar as demais
- Suportar múltiplos monitoramentos simultâneos

---

## Lifespan

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application started and ready for requests")
    yield
    logger.info("Application is shutting down. Cleaning up resources...")
```

Substitui os eventos `startup`/`shutdown` depreciados. Loga o início e encerramento da aplicação.

---

## Endpoints

### `GET /`

Serve a interface web principal.

```python
@app.get("/", response_class=HTMLResponse)
async def index():
    template_path = TEMPLATES_DIR / "index.html"
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logger.error(f"Template not found at: {template_path}")
        raise HTTPException(status_code=404, detail="Frontend template missing")
```

---

### `POST /start`

Inicia o monitoramento de um elemento. Se já existir uma task para a mesma URL, cancela e recria.

```python
@app.post("/start")
async def start_monitoring(req: MonitorRequest) -> Dict[str, str]:
    if req.url in active_tasks:
        active_tasks[req.url].cancel()
    task = asyncio.create_task(monitor_price(req.url, req.xpath))
    active_tasks[req.url] = task
    return {"message": "Monitoring started successfully"}
```

**Body:**
```json
{ "url": "https://site.com/produto", "xpath": "#preco > span:nth-of-type(1)", "username": "amanda" }
```

**Resposta:**
```json
{ "message": "Monitoring started successfully" }
```

---

### `POST /stop`

Cancela o monitoramento de uma URL específica.

```python
@app.post("/stop")
async def stop_monitoring(req: StopRequest) -> Dict[str, str]:
    if req.url in active_tasks:
        active_tasks[req.url].cancel()
        del active_tasks[req.url]
        return {"message": "Monitoring stopped successfully"}
    return {"message": "No active monitoring for this URL"}
```

**Body:**
```json
{ "url": "https://site.com/produto", "username": "amanda" }
```

---

### `WebSocket /ws/xpath`

Canal de comunicação para o Live Selector. Recebe uma URL e o nome do operador, dispara `open_live_selector()` e retorna o CSS selector capturado.

```python
@app.websocket("/ws/xpath")
async def xpath_websocket(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            url = data.get("url")
            username = data.get("username", "Desconhecido")
            if url:
                logger.info(f"[{username}] WebSocket: Starting Live Selector to {url}")
                asyncio.create_task(open_live_selector(url, websocket))
    except WebSocketDisconnect:
        logger.info("WebSocket: Client disconnected.")
    except Exception as e:
        logger.error(f"WebSocket Error: {e}")
```

**Mensagem recebida:**
```json
{ "url": "https://site.com", "username": "amanda" }
```

**Mensagem enviada ao receber o selector:**
```json
{ "type": "xpath_result", "xpath": "#preco > span:nth-of-type(1)" }
```

**Mensagem de erro:**
```json
{ "type": "error", "message": "..." }
```

---

## Configuração do Event Loop (Windows)

```python
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
```

!!! note
    No Windows, necessário para compatibilidade do Playwright com o event loop assíncrono do FastAPI/Uvicorn.

---

## Inicialização

```python
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
```

`reload=False` garante que o Playwright não tente recarregar workers em modo desenvolvimento.
