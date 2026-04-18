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

Este projeto é um assistente de lances automatizado desenvolvido como parte do Trabalho 01 da disciplina. O sistema tem como objetivo monitorar em tempo real o preço de um item em uma página web e, ao detectar uma alteração, interagir com uma segunda plataforma pública para registrar os valores antigo e novo. 

### Funcionalidades

* **Monitoramento Dinâmico:** O usuário informa a URL e o campo específico (via XPath, Regex, etc.) a ser analisado no momento da execução.
* **Notificação Automatizada:** Integração com sistemas públicos (ex: Gmail) para envio de informações sobre a alteração de preços e acionamento de botões de confirmação.
* **Log de Auditoria:** Registro completo de todas as ações realizadas pelo usuário durante a execução.
* **Validação de Dados:** Tratamento de erros para URLs inválidas, timeouts e consistência de tipos de dados (ex: verificar se a entrada é um número).
* **Testes Automatizados:** Suíte de testes unitários para garantir a estabilidade do código.

### Feito com

[![Python][Python]][Python-url]
[![FastAPI][FastAPI]][FastAPI-url]

---

## Primeiros Passos

Para obter uma cópia local deste projeto e colocá-la em funcionamento, siga estes passos simples.

### Especificações Técnicas

<!--Alterar quando definirmos-->
* **Linguagem de Programação:** [Inserir Linguagem, ex: Python].
* **Bibliotecas Utilizadas:** [Inserir Bibliotecas, ex: Selenium, BeautifulSoup, Pytest].
* **Documentação:** Gerada via [Inserir ferramenta, ex: Sphinx ou MkDocs].
* **Análise de Algoritmo:** Complexidade de tempo calculada em notação Big O.

### Critérios de Avaliação Atendidos

O projeto foi estruturado para cumprir os seguintes requisitos pontuáveis:

* **Localização de Variável (2 pts): Identificação do campo na página e log da posição (Xpath/Regex).**
* **Monitoramento (2 pts): Log no console de todas as alterações identificadas.**
* **Interação de Saída (2 pts): Registro em outra página e clique em botão.**
* **Documentação (1 pt): Uso de ferramentas de documentação automatizada.**
* **Log de Usuário (1 pt): Validação de nome de usuário (mínimo 3 caracteres alfabéticos) e histórico de ações.**
* **Qualidade Técnica (2 pts): Testes unitários automatizados e cálculo correto do Big O.**

### Como Executar

1.  **Clone o repositório:**
    ```bash
    https://github.com/Batsy13/stella-montis.git
    ```
2.  **Navegue para a pasta do projeto**
    ```bash
    cd projeto
    ```
3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt 
    ```
4.  **Instale os navegadores:**
    ```bash
    playwright install
    ```
5.  **Inicie a aplicação:**
    ```bash
    python main.py
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

<!--Alterar quando as linguagens-->
[Python]: https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54
[Python-url]: https://www.python.org/
[FastAPI]: https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi
[FastAPI-url]: https://fastapi.tiangolo.com/

