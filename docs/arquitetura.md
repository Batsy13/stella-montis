# Arquitetura do Sistema

## Visão Geral

O Stella Montis é uma aplicação **web monolítica assíncrona** construída sobre FastAPI. A comunicação entre o frontend (HTML/JS) e o backend (Python) ocorre via HTTP REST. O monitoramento é executado em **background tasks** do FastAPI, permitindo que o servidor continue responsivo enquanto o loop de polling roda em paralelo.

---

## Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────────┐
│                        NAVEGADOR (Cliente)                      │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    index.html                            │  │
│  │  ┌────────────┐  ┌───────────────────────────────────┐  │  │
│  │  │ URL Input  │  │           iframe                  │  │  │
│  │  │ Email Input│  │  (página alvo carregada via proxy) │  │  │
│  │  │ Load Page  │  │  • hover → borda vermelha          │  │  │
│  │  │ Start Mon. │  │  • click → borda azul + postMessage│  │  │
│  │  └────────────┘  └───────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
└───────────────────┬─────────────────────────────────────────────┘
                    │ HTTP (REST)
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FastAPI (app/main.py)                       │
│                                                                 │
│  GET  /          → serve index.html                             │
│  GET  /proxy     → carrega URL via Playwright, injeta scripts   │
│  POST /start     → dispara BackgroundTask: monitor_price()      │
└──────────┬──────────────────────────┬────────────────────────────┘
           │                          │
           ▼                          ▼
┌──────────────────────┐   ┌──────────────────────────────────────┐
│  Playwright Browser  │   │   monitor_service.monitor_price()    │
│  (Chromium headless) │   │                                      │
│                      │   │  loop:                               │
│  Usado em /proxy     │   │    ├─ page.locator(selector)         │
│  para renderizar     │   │    ├─ inner_text() → current_value   │
│  SPAs e sites com    │   │    ├─ comparar com last_value        │
│  JS pesado           │   │    └─ se mudou → send_email()        │
└──────────────────────┘   └──────────────┬───────────────────────┘
                                          │
                                          ▼
                            ┌─────────────────────────┐
                            │  email_service.send_email│
                            │  smtplib → Gmail SMTP   │
                            │  TLS (porta 587)         │
                            └─────────────────────────┘
                                          │
                                          ▼
                            ┌─────────────────────────┐
                            │  logger_config (Loguru) │
                            │  • stdout colorido       │
                            │  • logs/monitor_log.txt  │
                            │  • rotação em 10 MB      │
                            └─────────────────────────┘
```

---

## Decisões de Design

### Por que FastAPI?

- Suporte nativo a `async/await`, essencial para o Playwright assíncrono
- `BackgroundTasks` permite disparar o loop de monitoramento sem bloquear o servidor
- Validação automática de request bodies via Pydantic

### Por que Playwright (e não Selenium ou requests)?

- Lida com páginas **SPA** (React, Angular, Vue) que dependem de JavaScript para renderizar conteúdo
- Suporte nativo a `async/await`
- Permite extrair o HTML renderizado completo para o proxy iframe

### Por que o Proxy Iframe?

O problema central: o usuário não conhece previamente a estrutura da página. A solução foi carregar a página no backend via Playwright, limpar os headers de segurança (CSP, X-Frame-Options) e injetar JavaScript que:

1. Destaca elementos no hover (borda vermelha)
2. Captura o CSS selector do elemento clicado
3. Envia o selector para o frame pai via `postMessage`

Isso torna a seleção de elementos **completamente visual**, sem exigir conhecimento técnico do usuário.

### Por que Loguru (e não o `logging` padrão)?

- API mais simples: `logger.info()`, `logger.warning()`, etc.
- Formatação colorida no terminal sem configuração adicional
- Rotação e encoding UTF-8 configuráveis em uma linha
- Thread-safe com `enqueue=True`

---

## Modelo de Dados

### `MonitorRequest` (Pydantic)

```python
class MonitorRequest(BaseModel):
    url: str       # URL da página a monitorar
    xpath: str     # CSS selector do elemento (gerado pelo proxy)
    email: str     # E-mail para receber notificações
```

Validação automática pelo FastAPI: campos ausentes ou de tipo errado retornam HTTP 422.

---

## Fluxo de Dados Detalhado

### Fase 1 — Carregamento do Proxy

```
POST /proxy?url=https://site.com
  │
  ├─ Playwright abre Chrome headless
  ├─ Navega para a URL (timeout 60s)
  ├─ Aguarda 5s para JS renderizar
  ├─ Extrai HTML final (page.content())
  ├─ Remove: <meta CSP>, <meta X-Frame-Options>, <script>
  ├─ Injeta: <base href="url">, scripts de hover/click
  └─ Retorna HTML modificado → renderizado no iframe
```

### Fase 2 — Monitoramento

```
POST /start { url, xpath, email }
  │
  ├─ Envia e-mail "Monitoramento Iniciado"
  ├─ Abre Chrome headless (persistente)
  ├─ Navega para url
  └─ Loop (interval=10s):
       ├─ locator = page.locator(xpath).first
       ├─ current_value = locator.inner_text()
       ├─ Se last_value is None → salva valor inicial
       ├─ Se current_value != last_value:
       │    ├─ logger.warning(f"Changed: {old} → {new}")
       │    └─ send_email(email, subject, body)
       └─ asyncio.sleep(10)
```

---

## Tratamento de Erros

| Situação | Comportamento |
|---|---|
| Browser fechado pelo usuário | `PlaywrightError("closed")` → loop encerra graciosamente |
| Task cancelada | `asyncio.CancelledError` → log INFO, encerra |
| Qualquer outro erro | `Exception` → log ERROR, encerra |
| Falha no envio de e-mail | Erro logado, monitoramento continua |
| Credenciais SMTP ausentes | Log ERROR, função retorna `False` |
| Autenticação SMTP falha | `SMTPAuthenticationError` → log ERROR |
