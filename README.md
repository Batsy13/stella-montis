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

<img width="1887" height="1051" alt="image" src="https://github.com/user-attachments/assets/6f3f3356-00ac-4eab-b919-6143c93f476a" />

## Projeto

Este projeto é um assistente de lances automatizado desenvolvido como parte do Trabalho 01 da disciplina. O sistema monitora em tempo real o preço de um item em uma página web e, ao detectar uma alteração, interage com o Google Forms — uma plataforma pública que o sistema não controla — preenchendo e submetendo o formulário com os valores antigo e novo.

O usuário **não precisa conhecer previamente a estrutura da página**: basta informar a URL e clicar no elemento desejado através do **Live Selector**, um browser Chromium real aberto pelo sistema.

### Funcionalidades

* **Live Selector:** Abre um browser Chromium real na URL informada. O usuário clica no elemento desejado e o CSS selector é capturado automaticamente e enviado ao frontend via WebSocket.
* **Monitoramento Dinâmico:** Polling assíncrono a cada 10 segundos detecta alterações no valor do elemento selecionado.
* **Notificação via Google Forms:** Ao detectar mudança, preenche e submete um Google Form com o valor antigo e o novo — tanto por HTTP quanto abrindo o formulário visualmente no browser.
* **Start / Stop:** O monitoramento pode ser iniciado e interrompido pela interface sem reiniciar a aplicação.
* **Log de Auditoria:** Registro completo de todas as ações no console (colorido) e em arquivo `logs/monitor_log.txt` com rotação automática.

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
* **Comunicação em tempo real:** WebSocket (nativo FastAPI)
* **Automação de Browser:** Playwright (Chromium)
* **Notificações:** Google Forms via `requests` + Playwright
* **Logging:** Loguru — stdout colorido + arquivo rotativo (`logs/monitor_log.txt`)
* **Documentação:** MkDocs com tema Material
* **Análise de Algoritmo:** Complexidade de tempo O(n) e espaço O(1) para o loop de monitoramento

### Critérios de Avaliação Atendidos

O projeto foi estruturado para cumprir os seguintes requisitos pontuáveis:

* **Localização de Variável (2 pts):** Identificação visual do campo na página via Live Selector e log do CSS selector capturado.
* **Monitoramento (2 pts):** Log no console e em arquivo de todas as alterações identificadas.
* **Interação de Saída (2 pts):** Preenchimento e submissão do Google Forms com valor antigo e novo, incluindo clique no botão "Enviar".
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

4. **Inicie a aplicação:**
    ```bash
    cd app
    python main.py
    ```

5. Acesse **http://localhost:8000**, informe a URL, clique em **Sincronizar Interface de Captura**, selecione o elemento no browser que abrir e clique em **Iniciar Protocolo de Vigília**.

### Testes Automatizados

O projeto utiliza **pytest** para garantir a integridade das funções de monitoramento e comunicação.

1. **Executar todos os testes:**
   ```bash
   pytest
   ```
### Documentação Técnica

```bash
pip install mkdocs mkdocs-material
mkdocs serve
```

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

[Python]: https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54
[Python-url]: https://www.python.org/
[FastAPI]: https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi
[FastAPI-url]: https://fastapi.tiangolo.com/
[Playwright]: https://img.shields.io/badge/Playwright-2EAD33?style=for-the-badge&logo=playwright&logoColor=white
[Playwright-url]: https://playwright.dev/python/
[Loguru]: https://img.shields.io/badge/Loguru-2C2C2C?style=for-the-badge&logo=python&logoColor=white
[Loguru-url]: https://loguru.readthedocs.io/
[MkDocs]: https://img.shields.io/badge/MkDocs-526CFE?style=for-the-badge&logo=materialformkdocs&logoColor=white
[MkDocs-url]: https://squidfunk.github.io/mkdocs-material/
