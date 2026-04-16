# Histórico de Branches

Esta página documenta a evolução do projeto através das branches Git, descrevendo o que cada uma implementou e como as features foram integradas na branch `dev` (branch principal de desenvolvimento).

---

## Mapa de Branches

```
main ─────────────────────────────────────────────────────────► (README only)
  │
  └─ first commit (ece0d04)
       │
       ├─ feat: adds asset miner — Binance/TradingView (bb519fc)
       ├─ feat: adds asset miner — Google Finance (8a6830c)
       ├─ feat: adds asset miner — Infomoney/StatusInvest/Investidor10
       ├─ refactor: update imports/names (575a25a, 12ccfbe)
       │
       ├──► feat/interface ──────────────────────────────────────────────►
       │       feat: proxy interface + background monitor (cc20b9a)
       │
       ├──► feat/logging ──────────────────────────────────────────────►
       │       feat: txt logging for monitoring events (f7fbb9f)
       │
       ├──► feat/send-email ───────────────────────────────────────────►
       │       feat: email alerts for value changes (f859a4c)
       │       fix: add .env (5bbaa08)
       │       └── Merged into dev via PR #2
       │
       └──► dev ──────────────────────────────────────────────────────►
               Merge feat/send-email (84f4822)
               fix: change code structure / reorganize (1f39158)  ◄ HEAD
```

---

## Branch `main`

**Propósito:** Branch de apresentação pública. Contém apenas o `README.md`.

**Commits:**

| Hash | Mensagem | Autor |
|---|---|---|
| `a99822e` | Update README.md with center alignment | Pedro Costa |
| `a763e9d` | Refactor README with project name and student table | Pedro Costa |
| `8371ebc` | Alterando README com a primeira versão | — |
| `ece0d04` | first commit | — |

O README documenta o projeto, lista as funcionalidades planejadas, a tabela de alunos e os critérios de avaliação atendidos.

---

## Branch `feat/interface`

**Propósito:** Implementação da interface web e do proxy Playwright.

**Commit principal:** `cc20b9a — feat: implement proxy interface and background monitor`

### O que foi implementado

Esta foi a branch mais estrutural do projeto. Ela introduziu:

**1. Proxy de páginas (`GET /proxy`)**

O endpoint recebe uma URL, abre o Chromium headless via Playwright, aguarda o JavaScript renderizar, extrai o HTML completo e o re-serve com modificações:
- Remove CSP e X-Frame-Options (permitem embutir no iframe)
- Remove `<script>` existentes (evita conflitos)
- Injeta `<base href>` (corrige caminhos relativos)
- Injeta CSS de hover/seleção e JavaScript de `postMessage`

**2. Interface HTML (`index.html`)**

Página com campos de URL, iframe e botão de monitoramento. O script de `postMessage` recebe o selector do iframe e habilita o botão "Start Monitoring".

**3. Monitor básico (`monitor.py`)**

Versão inicial sem email e sem logging:

```python
async def monitor_price(url: str, selector: str, interval: int = 10):
    # Abre browser, navega, loop de polling com print() no console
    while True:
        current_value = await locator.inner_text()
        if current_value != last_value:
            print(f"Changed! Old: {last_value} | New: {current_value}")
```

**Estrutura de arquivos desta branch:**

```
stella-montis/
├── main.py          # FastAPI com endpoints /proxy e /start
├── monitor.py       # Loop de polling
├── index.html       # Interface web
└── br/com/stella-montis/dataminer/   # Miners específicos por site
    ├── binance.py
    ├── google.py
    ├── infomoney.py
    ├── investidor10.py
    ├── statusinvest.py
    └── tradingview.py
```

---

## Branch `feat/logging`

**Propósito:** Adicionar persistência de logs em arquivo `.txt`.

**Commit principal:** `f7fbb9f — feat(logging): add txt logging for monitoring events`

### O que foi implementado

Criação do módulo `logger_config.py` com Loguru:

```python
# Versão inicial
def setup_logger() -> None:
    logger.remove()
    logger.add(sys.stdout, level="INFO",
               format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")
    logger.add("monitor_log.txt", level="INFO",
               format="...", encoding="utf-8", enqueue=True, rotation="1 MB")
```

Esta branch substituiu os `print()` do `monitor.py` por chamadas ao `logger`, gerando:
- Saída formatada no terminal
- Arquivo `monitor_log.txt` com histórico persistente

**Diferença para a versão final (`dev`):**
- Rotação: 1 MB → 10 MB
- Sem `{name}:{function}:{line}` (adicionado na `dev`)
- Sem colorização no stdout (adicionado na `dev`)

---

## Branch `feat/send-email`

**Propósito:** Notificação por e-mail ao detectar mudança de valor.

**Commits:**

| Hash | Mensagem |
|---|---|
| `f859a4c` | feat: implement email alerts for monitored value changes |
| `5bbaa08` | fix: add .env |
| `af2f38c` | chore: update gitignore rules |

### O que foi implementado

**1. `email_service.py` (versão inicial)**

```python
def send_email(to_email: str, subject: str, message: str):
    sender_email = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")
    msg = MIMEText(message)
    # ... envio via smtp.gmail.com:587
```

Versão simples: sem MIMEMultipart, sem tratamento específico de erros, SMTP hardcoded para Gmail.

**2. Integração no monitor**

O `monitor.py` foi atualizado para chamar `send_email()` ao detectar mudança, enviando valor antigo e novo.

**3. Arquivos de ambiente**

Criação de `.env.example` e adição de `.env` ao `.gitignore`.

**Esta branch foi mergeada em `dev` via Pull Request #2.**

---

## Branch `dev`

**Propósito:** Branch principal de desenvolvimento. Integra todas as features e aplica refatorações de qualidade.

**Commits relevantes:**

| Hash | Mensagem |
|---|---|
| `84f4822` | Merge pull request #2 from Batsy13/feat/send-email |
| `1f39158` | fix: change code structure |

### Refatorações do commit `1f39158`

O commit de reestruturação reorganizou o projeto em uma estrutura modular:

**Antes (raiz do projeto):**
```
main.py
monitor.py
email_service.py
logger_config.py
index.html
```

**Depois (estrutura `app/`):**
```
app/
├── core/
│   └── logger_config.py
├── services/
│   ├── email_service.py
│   └── monitor_service.py
├── templates/
│   └── index.html
└── main.py
logs/
└── monitor_log.txt
```

**Melhorias na `dev` em relação às branches de feature:**

| Aspecto | feat/\* (inicial) | dev (final) |
|---|---|---|
| Estrutura | Arquivos na raiz | Módulos em `app/core/`, `app/services/` |
| Logger | `rotation="1 MB"`, sem cores | `rotation="10 MB"`, colorido, `{name}:{function}:{line}` |
| Email | `smtplib` hardcoded, sem retorno | Configurável via `.env`, retorna `bool`, erros específicos |
| Monitor | Sem e-mail de ciclo de vida | E-mails de início e fim do monitoramento |
| Erros | `except Exception: print(e)` | Tratamento específico por tipo de exceção |
| Windows | Sem configuração de event loop | `WindowsProactorEventLoopPolicy` |
| Email assíncrono | `send_email()` síncrono direto | `asyncio.to_thread()` para não bloquear o event loop |

---

## Linha do Tempo Consolidada

```
Abr 2026    Commit         Branch            O que mudou
──────────────────────────────────────────────────────────────────
Abr  4      ece0d04        main/dev          first commit
Abr  4      bb519fc        feat/interface    miners Binance/TradingView
Abr  4      8a6830c        feat/interface    miner Google Finance
Abr  4      f053b17        feat/interface    miner Infomoney
Abr  4      1b9fa1b        feat/interface    miner StatusInvest
Abr  4      e48abf7        feat/interface    miner Investidor10
Abr  4      575a25a        feat/interface    refactor nomes
Abr  4      cc20b9a        feat/interface    proxy + interface + monitor básico
Abr  4      f7fbb9f        feat/logging      logging em arquivo txt
Abr  4      af2f38c        feat/logging      gitignore
Abr  4      f859a4c        feat/send-email   email alerts
Abr  4      5bbaa08        feat/send-email   fix .env
Abr 15      84f4822        dev               merge feat/send-email (PR #2)
Abr 15      1f39158        dev               reestruturação modular (versão final)
```
