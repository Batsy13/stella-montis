# Stella Montis

**Assistente de Lances para Sites de Leilão**

---

## Visão Geral

O **Stella Montis** é um assistente de monitoramento de preços desenvolvido como trabalho prático da disciplina. O sistema monitora em tempo real o valor de qualquer campo em qualquer página web e, ao detectar uma alteração, notifica o usuário via e-mail com os valores antigo e novo.

O diferencial do projeto é que o usuário **não precisa conhecer previamente a estrutura da página**: basta informar a URL e clicar no elemento desejado através da interface visual interativa.

---

## Funcionalidades Principais

| Funcionalidade | Descrição |
|---|---|
| **Monitoramento dinâmico** | O usuário informa a URL em tempo de execução e seleciona visualmente o campo a monitorar |
| **Proxy inteligente** | A aplicação carrega a página alvo em um iframe e injeta scripts de seleção visual |
| **Detecção de mudança** | Polling assíncrono a cada 10 segundos compara o valor atual com o anterior |
| **Notificação por e-mail** | Ao detectar mudança, envia e-mail via Gmail SMTP com valor antigo e novo |
| **Log de auditoria** | Registra todas as ações em console e em arquivo `monitor_log.txt` |
| **Ciclo de vida completo** | E-mails são enviados também ao iniciar e ao encerrar o monitoramento |

---

## Stack Tecnológica

| Camada | Tecnologia |
|---|---|
| **Linguagem** | Python 3.11+ |
| **Framework Web** | FastAPI |
| **Automação de Browser** | Playwright (Chromium) |
| **E-mail** | smtplib + Gmail SMTP |
| **Logging** | Loguru |
| **Servidor** | Uvicorn (ASGI) |
| **Frontend** | HTML + JavaScript vanilla |
| **Documentação** | MkDocs + Material Theme |

---

## Equipe

| Nome | Matrícula |
|---|---|
| Amanda Ferreira Dahm | 2422130022 |
| Felipe Ferreira Lucas | 2312130021 |
| Gabriel Diogo Oliveira | 2222082011 |
| Gabriel Rodrigues de Oliveira | 2312130033 |
| João Marcos Santos e Carvalho | 2312130063 |
| Pedro Costa Ferreira | 2312130138 |

---

## Fluxo de Funcionamento

```
Usuário informa URL
        │
        ▼
Backend (FastAPI /proxy) carrega a página via Playwright
        │
        ▼
Página renderizada no iframe com scripts de seleção visual injetados
        │
        ▼
Usuário clica no elemento → CSS selector enviado via postMessage
        │
        ▼
Usuário clica "Start Monitoring" → POST /start
        │
        ▼
Background Task: monitor_price() roda em loop (a cada 10s)
        │
        ├─ Valor igual → aguarda próximo ciclo
        │
        └─ Valor diferente → send_email() + log de WARNING
```

---

!!! tip "Como começar"
    Consulte o [Guia de Instalação](instalacao.md) para configurar e executar o projeto localmente.
