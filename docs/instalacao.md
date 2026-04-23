# Instalação e Configuração

## Pré-requisitos

- Python 3.11 ou superior
- pip (gerenciador de pacotes Python)

---

## 1. Clonar o Repositório

```bash
git clone https://github.com/Batsy13/stella-montis.git
cd stella-montis
```

---

## 2. Criar e Ativar Ambiente Virtual

=== "Windows"
    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```

=== "Linux / macOS"
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

---

## 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

| Pacote | Finalidade |
|---|---|
| `fastapi` | Framework web ASGI com suporte nativo a WebSocket |
| `uvicorn` | Servidor ASGI |
| `uvicorn[standard]` | Instalação do Uvicorn com dependências extras de performance |
| `websockets` | Implementação de protocolo para comunicação bidirecional |
| `wsproto` | Parser de protocolo WebSocket para conformidade técnica |
| `pydantic` | Validação de dados nos modelos FastAPI |
| `loguru` | Logging estruturado |
| `playwright` | Automação de browser (Live Selector + monitoramento) |
| `requests` | Envio de notificações via HTTP POST ao Google Forms |
| `pytest` | Framework para criação e execução de testes automatizados |
| `pytest-asyncio` | Suporte a testes assíncronos para coroutines do Python |
| `httpx` | Cliente HTTP assíncrono para testes de integração de API |

Após instalar o playwright, baixe o browser:

```bash
playwright install chromium
```

---

## 4. Executar a Aplicação

```bash
cd app
python main.py
```

O servidor iniciará em `http://localhost:8000`.

---

## 5. Usar a Interface

1. Abra o navegador em **http://localhost:8000**
2. No campo **Coordenada de Origem (URL)**, insira a URL a monitorar
3. Clique em **Sincronizar Interface de Captura**
4. Um browser Chromium abrirá na página — clique no elemento desejado (hover vermelho, selecionado azul)
5. O CSS selector aparecerá automaticamente no campo **Vetor de Dados (XPath)**
6. Clique em **Iniciar Protocolo de Vigília** para começar o monitoramento
7. Para parar, clique em **Interromper Protocolo**

---

## 6. Gerar a Documentação (MkDocs)

```bash
pip install mkdocs mkdocs-material
mkdocs serve
```

Acesse em `http://127.0.0.1:8000` (porta padrão do MkDocs — use porta diferente se a aplicação estiver rodando).

Para gerar os arquivos estáticos:

```bash
mkdocs build
```

---

## Estrutura de Diretórios

```
stella-montis/
├── app/
│   ├── core/
│   │   └── logger_config.py        # Configuração do Loguru
│   ├── services/
│   │   ├── monitor_service.py      # Loop de monitoramento + notificação Google Forms
│   │   └── selector_service.py     # Live Selector via Playwright + WebSocket
│   ├── templates/
│   │   └── index.html              # Interface web (WebSocket client)
|   ├── tests/
│   │   └── conftest.py             # Gerencia fixtures globais e configurações do loop de eventos assíncronos para o ambiente de teste.
|   |   └── test_logger_config.py   # Valida a criação de diretórios, escrita de arquivos e o padrão de formatação dos logs.
|   |   └── test_main.py            # Testa os endpoints da API, o gerenciamento de tarefas ativas e a integridade das rotas /start e /stop.
|   |   └── test_monitor_service.py # Verifica a lógica de detecção de mudanças de preço e o tratamento de exceções no polling.
│   └── main.py                     # Entrada da aplicação (FastAPI + WebSocket)
├── logs/
│   └── monitor_log.txt             # Arquivo de log gerado em runtime
├── docs/                           # Documentação MkDocs
├── requirements.txt
├── mkdocs.yml
└── README.md
```
