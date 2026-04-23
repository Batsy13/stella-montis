# Testes Automatizados

**Caminho:** `app/tests/`  
**Responsabilidade:** Suite de testes com pytest cobrindo endpoints REST, lógica de monitoramento e configuração de logging.

---

## Estrutura

```
app/tests/
├── conftest.py            # Fixtures compartilhadas e configuração de mocks
├── test_main.py           # Testes de integração dos endpoints REST
├── test_monitor_service.py # Testes unitários de send_google_form
└── test_logger_config.py  # Testes unitários de setup_logger
```

---

## `conftest.py` — Fixtures Globais

A fixture `client` cria um `TestClient` do FastAPI com `monitor_price` e `open_live_selector` substituídos por `AsyncMock`, evitando que browsers reais abram durante os testes.

```python
@pytest.fixture
def client():
    with (
        patch("main.monitor_price", new_callable=AsyncMock),
        patch("main.open_live_selector", new_callable=AsyncMock),
    ):
        import main
        main.active_tasks.clear()
        with TestClient(main.app) as test_client:
            yield test_client
        main.active_tasks.clear()
```

O dicionário `active_tasks` é limpo antes e depois de cada teste para garantir isolamento.

---

## `test_main.py` — Endpoints REST

Testa os endpoints `GET /`, `POST /start` e `POST /stop`.

### `TestIndexEndpoint`

| Teste | O que verifica |
|---|---|
| `test_returns_html_or_404` | `GET /` retorna 200 ou 404 dependendo do template |
| `test_200_has_html_content_type` | Se 200, Content-Type deve ser `text/html` |

### `TestStartEndpoint`

| Teste | O que verifica |
|---|---|
| `test_valid_payload_returns_200` | Payload válido com `url`, `xpath`, `username` retorna 200 |
| `test_response_contains_message_key` | Resposta contém a chave `message` |
| `test_success_message_text` | Mensagem indica que o monitoramento foi iniciado |
| `test_missing_xpath_returns_422` | Sem `xpath` → HTTP 422 |
| `test_missing_url_returns_422` | Sem `url` → HTTP 422 |
| `test_empty_body_returns_422` | Body vazio → HTTP 422 |
| `test_duplicate_start_replaces_task` | Dois starts para a mesma URL funcionam sem erro |

### `TestStopEndpoint`

| Teste | O que verifica |
|---|---|
| `test_stop_nonexistent_url_returns_200` | Stop de URL não monitorada retorna 200 |
| `test_stop_nonexistent_url_message` | Mensagem informa ausência de monitoramento ativo |
| `test_stop_missing_url_returns_422` | Body vazio → HTTP 422 |
| `test_start_then_stop_lifecycle` | Ciclo completo start → stop funciona corretamente |
| `test_stop_removes_task_from_active` | Após stop, URL removida de `active_tasks` |

---

## `test_monitor_service.py` — `send_google_form`

Testa a função de envio HTTP ao Google Forms via mock de `requests.post`.

| Teste | O que verifica |
|---|---|
| `test_calls_post_once` | Exatamente uma chamada POST por invocação |
| `test_calls_correct_url` | URL de destino é o endpoint correto do Google Forms |
| `test_sends_message_in_correct_field` | Campo `entry.1608177186` contém exatamente o texto enviado |
| `test_handles_generic_exception_without_raising` | Exceção genérica não propaga |
| `test_handles_connection_error_without_raising` | `ConnectionError` não propaga |
| `test_handles_timeout_without_raising` | `Timeout` não propaga |
| `test_empty_message_still_calls_post` | Mensagem vazia é enviada normalmente |
| `test_multiline_message_preserved` | Quebras de linha chegam intactas |
| `test_special_characters_in_message` | Acentos e símbolos não causam erros |

---

## `test_logger_config.py` — `setup_logger`

Testa a configuração do Loguru em diferentes cenários.

| Teste | O que verifica |
|---|---|
| `test_default_level_does_not_raise` | Chamada sem argumentos (INFO) não lança exceção |
| `test_debug_level_does_not_raise` | Nível DEBUG aceito sem erro |
| `test_warning_level_does_not_raise` | Nível WARNING aceito sem erro |
| `test_error_level_does_not_raise` | Nível ERROR aceito sem erro |
| `test_idempotent_multiple_calls` | Múltiplas chamadas sequenciais não causam erro |
| `test_log_directory_exists_after_setup` | Diretório `logs/` criado após configuração |
| `test_log_file_is_created` | Arquivo `logs/monitor_log.txt` existe após configuração |

---

## Como Executar

```bash
cd app
pytest
```

Para ver saída detalhada:

```bash
pytest -v
```

Para executar um arquivo específico:

```bash
pytest tests/test_main.py -v
```

---

## Estratégia de Mock

Os testes **não lançam browsers reais**. As funções que invocam o Playwright são substituídas por `AsyncMock`:

- `monitor_price` → mockado no `conftest.py` para todos os testes de `main.py`
- `open_live_selector` → mockado no `conftest.py` para todos os testes de `main.py`
- `requests.post` → mockado individualmente em cada teste de `test_monitor_service.py`

Isso garante que os testes sejam rápidos, determinísticos e executáveis em qualquer ambiente (incluindo CI) sem dependência de browser instalado.

---

## CI — GitHub Actions

O workflow de CI executa `pytest` automaticamente a cada push e pull request, garantindo que nenhuma regressão chegue ao repositório sem ser detectada.
