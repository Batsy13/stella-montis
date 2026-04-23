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
               feat: add stop monitoring functionality + task management + UI toggle
               docs: add MkDocs documentation and update README
               feat: adiciona suite de testes pytest (30 casos)
               docs: refactor docstrings to english
               ci: add github actions workflow for automated testing
               ci: fix versions
               docs: add Google-style docstrings and improve PEP 8 compliance
               feat: update WebSocket URL logic
               feat: add username field to monitoring requests and include operator identity in logs
               test: add username field to API request payloads  ◄ HEAD
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

#### `feat: adiciona suite de testes pytest (30 casos)`

- Criação de `app/tests/` com `conftest.py`, `test_main.py`, `test_monitor_service.py`, `test_logger_config.py`
- Mocking de `monitor_price` e `open_live_selector` via `unittest.mock.AsyncMock`
- Testes cobrem: endpoints REST, validação Pydantic, ciclo de vida das tasks, `send_google_form`, `setup_logger`

#### `ci: add github actions workflow for automated testing`

- Workflow `.github/workflows/` para rodar `pytest` em CI
- Executa automaticamente a cada push e pull request

#### `docs: add Google-style docstrings and improve PEP 8 compliance`

- Docstrings no estilo Google adicionadas a todas as funções e classes
- Conformidade com PEP 8 aplicada em todo o código

#### `feat: add username field to monitoring requests and include operator identity in logs`

- Campo `username: str` adicionado a `MonitorRequest` e `StopRequest`
- `monitor_price()` recebe `username` como parâmetro (padrão `"Anônimo"`)
- Logs agora incluem `[username]` para rastreabilidade do operador
- Mensagens do Google Forms incluem o nome do operador
- WebSocket handler lê `username` da mensagem recebida

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
Abr 15     54f58da   dev             stop monitoring + task management + UI toggle
Abr 15     3501dcb   dev             docs: MkDocs + README
Abr 15     8bfd88e   dev             feat: suite de testes pytest (30 casos)
Abr 15     7db54d0   dev             docs: docstrings refatoradas para inglês
Abr 15     477f10b   dev             ci: github actions workflow
Abr 15     00fa077   dev             ci: fix versions
Abr 15     b681aaf   dev             docs: docstrings Google-style + PEP 8
Abr 22     781dcd6   dev             feat: update WebSocket URL logic
Abr 22     34ee422   dev             feat: username em requests + logs com identidade do operador
Abr 22     74953e9   main            Update image in README.md
Abr 22     b899298   dev             test: username nos payloads dos testes  ◄ HEAD
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
| Rastreabilidade | Sem identificação de operador | Campo `username` em todos os requests e logs |
| Testes | Sem cobertura | Suite pytest com 30 casos (unit + integração) |
| CI | Sem pipeline | GitHub Actions: pytest automático em cada push/PR |
