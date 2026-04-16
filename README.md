<div align="center">
  
# Stella-Montis

</div>
<a id="readme-top"></a>

<br />
<details>
  <summary>Tabela de Conteúdos</summary>
  <ol>
    <li>
      <a href="#projeto">Projeto</a>
      <ul>
        <li><a href="#funcionalidades">Funcionalidades</a></li>
        <li><a href="#feito-com">Feito com</a></li>
      </ul>
    </li>
    <li>
      <a href="#primeiros-passos">Primeiros Passos</a>
      <ul>
        <li><a href="#especificações-técnicas">Especificações Técnicas</a></li>
        <li><a href="#critérios-de-avaliação-atendidos">Critérios de Avaliação Atendidos</a></li>
        <li><a href="#como-executar">Como Executar</a></li>
      </ul>
    </li>
    <li><a href="#alunos">Alunos</a></li>
  </ol>
</details>

---

## Projeto

Este projeto é um assistente de lances automatizado desenvolvido como parte do Trabalho 01 da disciplina. O sistema monitora em tempo real o preço de um item em uma página web e, ao detectar uma alteração, notifica o usuário via e-mail com os valores antigo e novo.

O diferencial do projeto é que o usuário **não precisa conhecer previamente a estrutura da página**: basta informar a URL e clicar no elemento desejado através da interface visual interativa.

### Funcionalidades

* **Monitoramento Dinâmico:** O usuário informa a URL e seleciona visualmente o campo a ser monitorado em tempo de execução, sem necessidade de conhecimento técnico da página.
* **Proxy Inteligente:** A aplicação carrega a página alvo via Playwright e a exibe em um iframe com scripts de seleção visual injetados (hover em vermelho, seleção em azul).
* **Notificação por E-mail:** Integração com Gmail via SMTP — envia e-mail ao detectar mudança de valor, informando o valor antigo e o novo. E-mails também são enviados ao iniciar e encerrar o monitoramento.
* **Log de Auditoria:** Registro completo de todas as alterações no console (colorido) e em arquivo `logs/monitor_log.txt` com rotação automática.
* **Tratamento de Erros:** Tratamento específico para browser fechado, cancelamento de tarefa e falhas de autenticação SMTP.

### Feito com

[![Python][Python]][Python-url]
[![FastAPI][FastAPI]][FastAPI-url]
[![Playwright][Playwright]][Playwright-url]
[![Loguru][Loguru]][Loguru-url]
[![MkDocs][MkDocs]][MkDocs-url]

---

## Primeiros Passos

Para obter uma cópia local deste projeto e colocá-la em funcionamento, siga estes passos simples.

### Especificações Técnicas

* **Linguagem de Programação:** Python 3.11+
* **Framework Web:** FastAPI + Uvicorn (ASGI)
* **Automação de Browser:** Playwright (Chromium)
* **Notificações:** smtplib via Gmail SMTP (TLS porta 587)
* **Logging:** Loguru — stdout colorido + arquivo rotativo (`logs/monitor_log.txt`)
* **Documentação:** MkDocs com tema Material
* **Análise de Algoritmo:** Complexidade de tempo O(n) e espaço O(1) para o loop de monitoramento

### Critérios de Avaliação Atendidos

O projeto foi estruturado para cumprir os seguintes requisitos pontuáveis:

* **Localização de Variável (2 pts):** Identificação visual do campo na página e log da posição (CSS selector).
* **Monitoramento (2 pts):** Log no console e em arquivo de todas as alterações identificadas.
* **Interação de Saída (2 pts):** Envio de e-mail via Gmail com valor antigo e novo ao detectar mudança.
* **Documentação (1 pt):** Documentação técnica completa gerada com MkDocs (tema Material).
* **Log de Usuário (1 pt):** Histórico de ações persistido em `logs/monitor_log.txt` com rotação automática.
* **Qualidade Técnica (2 pts):** Análise de complexidade Big O documentada; tratamento de erros por tipo de exceção.

### Como Executar

1. **Clone o repositório:**
    ```bash
    git clone https://github.com/Batsy13/stella-montis.git
    cd stella-montis
    ```

2. **Crie e ative o ambiente virtual:**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Linux/macOS
    source venv/bin/activate
    ```

3. **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    playwright install chromium
    ```

4. **Configure as variáveis de ambiente:**
    ```bash
    cp .env.example .env
    # Edite o .env com suas credenciais do Gmail
    ```

    ```dotenv
    EMAIL_USER=seu_email@gmail.com
    EMAIL_PASS=sua_app_password
    EMAIL_SMTP_SERVER=smtp.gmail.com
    EMAIL_SMTP_PORT=587
    ```

    > ⚠️ O campo `EMAIL_PASS` deve ser uma **App Password** do Google, não a senha normal da conta. Gere em: [myaccount.google.com/security](https://myaccount.google.com/security) → Verificação em duas etapas → Senhas de app.

5. **Inicie a aplicação:**
    ```bash
    cd app
    python main.py
    ```

6. Acesse **http://localhost:8000**, informe a URL e o e-mail, clique no elemento desejado e inicie o monitoramento.

### Documentação Técnica

Para visualizar a documentação completa do projeto:

```bash
pip install mkdocs mkdocs-material
mkdocs serve
```

Acesse em **http://127.0.0.1:8000** (porta padrão do MkDocs).

---

## Alunos

Segue o grupo responsável pelo desenvolvimento do projeto.

| Nome | Matrícula |
|------|--------|
| Amanda Ferreira Dahm | 2422130022 |
| Felipe Ferreira Lucas | 2312130021 |
| Gabriel Diogo Oliveira | 2222082011 |
| Gabriel Rodrigues de Oliveira | 2312130033 |
| João Marcos Santos e Carvalho | 2312130063 |
| Pedro Costa Ferreira | 2312130138 |

<p align="right">(<a href="#readme-top">voltar ao início</a>)</p>

[Python]: https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white
[Python-url]: https://www.python.org/
[FastAPI]: https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white
[FastAPI-url]: https://fastapi.tiangolo.com/
[Playwright]: https://img.shields.io/badge/Playwright-2EAD33?style=for-the-badge&logo=playwright&logoColor=white
[Playwright-url]: https://playwright.dev/python/
[Loguru]: https://img.shields.io/badge/Loguru-2C2C2C?style=for-the-badge&logo=python&logoColor=white
[Loguru-url]: https://loguru.readthedocs.io/
[MkDocs]: https://img.shields.io/badge/MkDocs-526CFE?style=for-the-badge&logo=materialformkdocs&logoColor=white
[MkDocs-url]: https://squidfunk.github.io/mkdocs-material/
