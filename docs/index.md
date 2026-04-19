# Stella Montis

**Assistente de Lances para Sites de Leilão**

---

## Visão Geral

O **Stella Montis** é um assistente de monitoramento de preços desenvolvido como trabalho prático da disciplina. O sistema monitora em tempo real o valor de qualquer campo em qualquer página web e, ao detectar uma alteração, notifica via **Google Forms** com os valores antigo e novo.

O usuário **não precisa conhecer previamente a estrutura da página**: basta informar a URL e clicar no elemento desejado através do **Live Selector** — um browser real aberto pelo sistema onde o elemento é selecionado visualmente.

---

## Funcionalidades Principais

| Funcionalidade | Descrição |
|---|---|
| **Live Selector** | Abre um browser real (Chromium) na URL informada; o usuário clica no elemento e o CSS selector é capturado automaticamente via WebSocket |
| **Monitoramento dinâmico** | Polling assíncrono a cada 10 segundos compara o valor atual com o anterior |
| **Notificação via Google Forms** | Ao detectar mudança, preenche e submete um Google Form com o valor antigo e novo — tanto via HTTP quanto abrindo o formulário visualmente |
| **Start / Stop** | O monitoramento pode ser iniciado e interrompido pela interface sem reiniciar a aplicação |
| **Gerenciamento de tasks** | Múltiplas URLs podem ser monitoradas simultaneamente; cada task é indexada pela URL |
| **Log de auditoria** | Registra todas as ações em console colorido e em arquivo `logs/monitor_log.txt` com rotação automática |

---

## Stack Tecnológica

| Camada | Tecnologia |
|---|---|
| **Linguagem** | Python 3.11+ |
| **Framework Web** | FastAPI |
| **Comunicação em tempo real** | WebSocket (nativo FastAPI) |
| **Automação de Browser** | Playwright (Chromium) |
| **Notificação** | Google Forms via `requests` + Playwright |
| **Logging** | Loguru |
| **Servidor** | Uvicorn (ASGI) |
| **Frontend** | HTML + JavaScript vanilla (WebSocket client) |
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
Clica "Sincronizar Interface de Captura"
        │
        ▼
WebSocket envia URL → selector_service.open_live_selector()
        │
        ▼
Chromium abre a página real (sem proxy, sem iframe)
Scripts injetados via add_init_script(): hover vermelho, click azul
        │
        ▼
Usuário clica no elemento → CSS selector enviado via sendToPython()
        │
        ▼
WebSocket retorna { type: "xpath_result", xpath: "..." } ao frontend
        │
        ▼
Usuário clica "Iniciar Protocolo de Vigília" → POST /start
        │
        ▼
asyncio.create_task(monitor_price()) registrado em active_tasks[url]
        │
        ├─ Valor igual → aguarda próximo ciclo (10s)
        │
        └─ Valor diferente → send_google_form() + show_visual_form()
                                    │
                                    └─ Preenche e submete Google Form
```

---

!!! tip "Como começar"
    Consulte o [Guia de Instalação](instalacao.md) para configurar e executar o projeto localmente.
