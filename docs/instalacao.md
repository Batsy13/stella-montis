# Instalação e Configuração

## Pré-requisitos

- Python 3.11 ou superior
- pip (gerenciador de pacotes Python)
- Conta Gmail com **App Password** habilitado (para envio de e-mails)

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

Dependências principais utilizadas no projeto:

| Pacote | Versão recomendada | Finalidade |
|---|---|---|
| `fastapi` | ≥ 0.110 | Framework web ASGI |
| `uvicorn` | ≥ 0.29 | Servidor ASGI |
| `playwright` | ≥ 1.43 | Automação de browser |
| `loguru` | ≥ 0.7 | Logging estruturado |
| `python-dotenv` | ≥ 1.0 | Leitura de variáveis de ambiente |
| `pydantic` | ≥ 2.0 | Validação de dados (modelos FastAPI) |

Após instalar o playwright, é necessário baixar o browser:

```bash
playwright install chromium
```

---

## 4. Configurar Variáveis de Ambiente

Copie o arquivo `.env.example` e preencha com suas credenciais:

```bash
cp .env.example .env
```

Edite o arquivo `.env`:

```dotenv
EMAIL_USER=seu_email@gmail.com
EMAIL_PASS=sua_app_password_aqui
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
```

!!! warning "Importante: App Password do Gmail"
    O campo `EMAIL_PASS` **não deve ser** a senha normal da conta Google.
    Você precisa gerar uma **App Password** (Senha de App):

    1. Acesse [myaccount.google.com/security](https://myaccount.google.com/security)
    2. Ative a **Verificação em duas etapas** (se ainda não estiver ativa)
    3. Em **"Como você faz login no Google"**, clique em **Senhas de app**
    4. Gere uma nova senha para o app "Mail"
    5. Use essa senha de 16 caracteres no `EMAIL_PASS`

!!! danger "Segurança"
    Nunca commite o arquivo `.env` no repositório. Ele já está listado no `.gitignore`.

---

## 5. Executar a Aplicação

```bash
cd app
python main.py
```

O servidor iniciará em `http://localhost:8000`.

---

## 6. Usar a Interface

1. Abra o navegador em **http://localhost:8000**
2. No campo **URL**, insira o endereço da página a monitorar
3. No campo **E-mail**, insira o endereço que receberá as notificações
4. Clique em **Load Page** — a página será carregada no iframe
5. **Clique no elemento** que deseja monitorar (ele ficará destacado em azul)
6. O seletor CSS aparecerá em **Target XPath**
7. Clique em **Start Monitoring** para iniciar

---

## 7. Gerar a Documentação (MkDocs)

Para visualizar esta documentação localmente:

```bash
pip install mkdocs mkdocs-material
mkdocs serve
```

Acesse em `http://127.0.0.1:8000` (porta padrão do MkDocs).

Para gerar os arquivos estáticos:

```bash
mkdocs build
```

Os arquivos serão gerados na pasta `site/`.

---

## Estrutura de Diretórios

```
stella-montis/
├── app/
│   ├── core/
│   │   └── logger_config.py      # Configuração do Loguru
│   ├── services/
│   │   ├── email_service.py      # Envio de e-mails via SMTP
│   │   └── monitor_service.py    # Loop de monitoramento
│   ├── templates/
│   │   └── index.html            # Interface web do usuário
│   └── main.py                   # Entrada da aplicação (FastAPI)
├── logs/
│   └── monitor_log.txt           # Arquivo de log gerado em runtime
├── docs/                         # Documentação MkDocs (este site)
├── .env.example                  # Template de variáveis de ambiente
├── .gitignore
├── mkdocs.yml
└── README.md
```
