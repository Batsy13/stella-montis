# Arquitetura do Sistema

## Visão Geral

O Stella Montis é uma aplicação **web assíncrona** construída sobre FastAPI. A comunicação entre o frontend e o backend ocorre via **HTTP REST** e **WebSocket**. O monitoramento roda em `asyncio.Task` registradas em um dicionário, permitindo start/stop por URL. A seleção de elementos usa um browser Chromium real (sem proxy/iframe), comunicando o resultado via WebSocket.

---

## Diagrama de Componentes

```
┌──────────────────────────────────────────────────────────────────┐
│                      NAVEGADOR (Cliente)                         │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                      index.html                           │  │
│  │                                                            │  │
│  │  [URL Input]   [Sincronizar Interface de Captura]          │  │
│  │  [XPath Input — readonly, preenchido via WebSocket]        │  │
│  │  [Iniciar Protocolo de Vigília]  [Interromper Protocolo]   │  │
│  │                                                            │  │
│  │  WebSocket Client ◄──────────────────────────────────────► │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────┬───────────────────────────────────────────┘
                       │ HTTP REST + WebSocket
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│                    FastAPI (app/main.py)                         │
│                                                                  │
│  GET  /           → serve index.html                             │
│  POST /start      → cria asyncio.Task → monitor_price()          │
│  POST /stop       → cancela Task por URL                         │
│  WS   /ws/xpath   → recebe URL, dispara open_live_selector()     │
│                                                                  │
│  active_tasks: Dict[str, asyncio.Task]  ← gerencia por URL      │
└──────┬────────────────────────┬─────────────────────────────────┘
       │                        │
       ▼                        ▼
┌──────────────────┐   ┌────────────────────────────────────────┐
│ selector_service │   │  monitor_service.monitor_price()       │
│                  │   │                                        │
│ Abre Chromium    │   │  loop (10s):                           │
│ real na URL      │   │   ├─ page.locator(selector)            │
│                  │   │   ├─ inner_text() → current_value      │
│ Injeta scripts   │   │   ├─ compara com last_value            │
│ via             │   │   └─ se mudou:                          │
│ add_init_script  │   │       ├─ send_google_form() (HTTP)     │
│                  │   │       └─ show_visual_form() (browser)  │
│ click → CSS      │   │                                        │
│ selector via     │   └──────────────────┬─────────────────────┘
│ sendToPython()   │                      │
│                  │              Google Forms
│ WebSocket ──────►│         (formulário público)
│ { xpath_result } │
└──────────────────┘
       ▲
       │ WebSocket
       └──────────────────── Frontend
```

---

## Decisões de Design

### Por que Live Selector em vez de Proxy Iframe?

A abordagem anterior carregava a página via Playwright, removia headers de segurança e re-servia o HTML em um iframe. Isso falhava em sites que carregavam **fontes externas e folhas de estilo via CDN**, pois a remoção dos scripts e a mudança de contexto quebravam o layout.

A solução atual abre a página diretamente em um **browser Chromium real**, sem nenhuma modificação no HTML. Os scripts de seleção são injetados via `add_init_script()`, que roda antes de qualquer script da página, garantindo compatibilidade universal.

### Por que WebSocket para o selector?

O `add_init_script()` roda no contexto do browser. Para trazer o CSS selector de volta ao Python, é necessário um canal de comunicação. `page.expose_function("sendToPython", callback)` expõe uma função Python ao JavaScript do browser — ao ser chamada, o dado chega via callback assíncrono. O WebSocket carrega esse resultado de volta ao frontend em tempo real.

### Por que Google Forms em vez de e-mail?

Google Forms é uma plataforma pública que o sistema não controla — atende ao requisito do trabalho de "interagir com outra página pública e clicar em um botão". A notificação é feita de duas formas complementares:

- **`send_google_form()`** — POST HTTP direto ao endpoint de resposta do Forms (silencioso, rápido)
- **`show_visual_form()`** — Playwright abre o formulário visualmente, preenche o campo e clica em "Enviar" (demonstrável)

### Por que `active_tasks` como `Dict[str, asyncio.Task]`?

Permite múltiplos monitoramentos simultâneos indexados por URL, e viabiliza o endpoint `/stop` que cancela uma task específica sem afetar as demais.

---

## Modelo de Dados

### `MonitorRequest` — `POST /start`

```python
class MonitorRequest(BaseModel):
    url: str    # URL da página monitorada
    xpath: str  # CSS selector do elemento (capturado pelo Live Selector)
```

### `StopRequest` — `POST /stop`

```python
class StopRequest(BaseModel):
    url: str    # URL cujo monitoramento deve ser encerrado
```

---

## Fluxo de Dados Detalhado

### Fase 1 — Live Selector (captura do CSS selector)

```
Frontend: ws.send({ url })
        │
        ▼
/ws/xpath recebe → asyncio.create_task(open_live_selector(url, websocket))
        │
        ▼
selector_service:
  ├─ Abre Chromium headless=False
  ├─ page.expose_function("sendToPython", on_xpath_selected)
  ├─ page.add_init_script(...)   ← CSS hover/click + cálculo do selector
  ├─ page.goto(url, wait_until="domcontentloaded", timeout=60s)
  └─ aguarda browser conectado (loop asyncio.sleep(1))

Usuário clica no elemento:
  └─ JS: window.sendToPython(xpath)
       └─ Python: on_xpath_selected(xpath)
            └─ websocket.send_json({ type: "xpath_result", xpath })
                 └─ Frontend: preenche campo XPath
```

### Fase 2 — Monitoramento

```
POST /start { url, xpath }
  │
  ├─ Cancela task anterior para a mesma URL (se existir)
  ├─ asyncio.create_task(monitor_price(url, xpath))
  └─ active_tasks[url] = task

monitor_price():
  ├─ Abre Chromium headless=False
  ├─ page.goto(url)
  └─ Loop (10s):
       ├─ locator.inner_text() → current_value
       ├─ Igual → sleep(10)
       └─ Diferente:
            ├─ logger.info(log_msg)
            ├─ asyncio.create_task(show_visual_form(message))
            └─ asyncio.to_thread ou create_task(send_google_form(message))
```

### Fase 3 — Stop

```
POST /stop { url }
  │
  ├─ active_tasks[url].cancel()
  └─ del active_tasks[url]
```

---

## Tratamento de Erros

| Situação | Comportamento |
|---|---|
| Browser fechado manualmente | `"closed" in str(e)` → loop encerra graciosamente |
| Task cancelada via `/stop` | `CancelledError` → bloco `finally` envia form de encerramento |
| URL não monitorada em `/stop` | Retorna mensagem informativa sem erro |
| Template HTML não encontrado | `HTTPException 404` |
| Erro no Google Forms | `logger.error()`, monitoramento continua |
| WebSocket desconectado | `WebSocketDisconnect` capturado, log INFO |
