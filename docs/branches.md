# Histórico de Branches

---

## Mapa de Branches

```
main ──────────────────────────────────────────────────────────► (README + docs)
  │
  └─ first commit
       │
       ├─ feat: miners Binance/TradingView/Google/Infomoney/StatusInvest/Investidor10
       ├─ refactor: update imports/names
       │
       ├──► feat/interface ──────────────────────────────────────────────────►
       │       feat: proxy interface + background monitor
       │
       ├──► feat/logging ───────────────────────────────────────────────────►
       │       feat: txt logging for monitoring events
       │
       ├──► feat/send-email ────────────────────────────────────────────────►
       │       feat: email alerts for value changes
       │       └── Merged into dev via PR #2
       │
       └──► dev ────────────────────────────────────────────────────────────►
               Merge feat/send-email (PR #2)
               fix: change code structure (reorganização modular)
               feat: add requirements configuration
               feat: improve interface and change proxy-based UI
               feat(ui): add persistent blue highlight
               feat: remove email and integrate Google Forms automation
               fix: remove env and improve forms logic
               Merge branch 'feat/send-email' into dev
               feat: add stop monitoring functionality + task management + UI toggle  ◄ HEAD
```

---

## Branch `main`

**Propósito:** Branch de apresentação pública. Contém README e documentação.

| Hash | Mensagem |
|---|---|
| `a99822e` | Update README.md with center alignment |
| `a763e9d` | Refactor README with project name and student table |
| `8371ebc` | Alterando README com a primeira versão |

---

## Branch `feat/interface`

**Propósito:** Primeira implementação da interface web e do proxy Playwright.

**O que foi implementado:**
- Endpoint `GET /proxy` que carrega URL via Playwright e re-serve HTML com scripts de seleção visual injetados
- Interface HTML com iframe proxy e captura de CSS selector via `postMessage`
- Monitor básico com `print()` no console (sem logging, sem email)
- Miners específicos por site: Binance, TradingView, Google Finance, Infomoney, StatusInvest, Investidor10

**Limitação identificada:** a abordagem de proxy iframe quebrava em sites com fontes externas e CDNs, pois remoção de scripts e mudança de contexto afetavam o carregamento de recursos externos.

---

## Branch `feat/logging`

**Propósito:** Adicionar persistência de logs em arquivo.

**O que foi implementado:**
- `logger_config.py` com Loguru
- Rotação em 1 MB, `enqueue=True` para thread-safety
- Substituição dos `print()` por `logger.info/warning/error`

---

## Branch `feat/send-email`

**Propósito:** Notificação por e-mail ao detectar mudança.

**O que foi implementado:**
- `email_service.py` com `smtplib` + Gmail SMTP
- Integração no `monitor_price()` com envio de valor antigo e novo
- `.env.example` com `EMAIL_USER`, `EMAIL_PASS`, `EMAIL_SMTP_SERVER`, `EMAIL_SMTP_PORT`

**Mergeada em `dev` via Pull Request #2.**

---

## Branch `dev`

**Propósito:** Branch principal de desenvolvimento. Integra todas as features e aplica evoluções arquiteturais.

### Evolução dos commits relevantes

#### `fix: change code structure` — reorganização modular

Reestruturou o projeto de arquivos na raiz para módulos em `app/`:

```
Antes:          Depois:
main.py     →   app/main.py
monitor.py  →   app/services/monitor_service.py
email_service.py → app/services/email_service.py
logger_config.py → app/core/logger_config.py
index.html  →   app/templates/index.html
```

#### `feat: improve interface and change proxy-based UI`

Substituiu o proxy iframe pelo **Live Selector**:
- `app/services/selector_service.py` criado
- Endpoint `/proxy` removido
- Endpoint WebSocket `/ws/xpath` adicionado
- `page.expose_function` + `page.add_init_script` em vez de HTML re-servido
- **Resolve a limitação de sites com fontes/estilos externos**

#### `feat: remove email and integrate Google Forms automation`

Substituiu o serviço de e-mail pelo **Google Forms**:
- `email_service.py` removido
- `send_google_form()` — POST HTTP ao endpoint de resposta
- `show_visual_form()` — Playwright preenche e submete o formulário visualmente
- Remoção da dependência de `.env` (sem credenciais necessárias)

#### `fix: remove env and improve forms logic`

- Remove `.env` e credenciais de e-mail do projeto
- Melhora a lógica de envio dos formulários

#### `feat: add stop monitoring functionality with task management and UI toggle`

- `active_tasks: Dict[str, asyncio.Task]` adicionado ao `main.py`
- Endpoint `POST /stop` adicionado
- Frontend: botão "Interromper Protocolo" com toggle start/stop
- Permite encerrar monitoramento sem reiniciar a aplicação

---

## Linha do Tempo Consolidada

```
Data       Hash      Branch          O que mudou
──────────────────────────────────────────────────────────────────────
Abr  4     ece0d04   main/dev        first commit
Abr  4     bb519fc   feat/interface  miners Binance/TradingView
Abr  4     cc20b9a   feat/interface  proxy + interface + monitor básico
Abr  4     f7fbb9f   feat/logging    logging em arquivo txt
Abr  4     f859a4c   feat/send-email email alerts
Abr 15     84f4822   dev             merge feat/send-email (PR #2)
Abr 15     1f39158   dev             reorganização modular (app/)
Abr 15     b536d64   dev             requirements.txt
Abr 15     a42e6bd   dev             melhoria da interface
Abr 15     d3dd75d   dev             highlight azul persistente no selector
Abr 15     87487cb   dev             Live Selector + Google Forms (remove email)
Abr 15     c83fcac   dev             remove .env, melhora lógica de forms
Abr 15     484ffcb   dev             merge feat/send-email
Abr 15     54f58da   dev             stop monitoring + task management + UI toggle  ◄ HEAD
```

---

## Comparativo: Versão Inicial vs. Atual

| Aspecto | Versão inicial (feat/\*) | Versão atual (dev HEAD) |
|---|---|---|
| Seleção de elementos | Proxy iframe com HTML modificado | Live Selector: browser real + WebSocket |
| Compatibilidade de sites | Quebrava com CDN/fontes externas | Universal |
| Notificação | E-mail via Gmail SMTP | Google Forms (HTTP + visual) |
| Credenciais | `.env` com EMAIL_USER/PASS | Nenhuma — sem credenciais |
| Stop monitoring | Sem suporte | `POST /stop` + `active_tasks` |
| Comunicação frontend | HTTP REST + postMessage (iframe) | HTTP REST + WebSocket |
| Estrutura | Arquivos na raiz | Módulos em `app/core/`, `app/services/` |
