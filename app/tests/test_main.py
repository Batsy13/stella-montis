"""
Testes de integração para os endpoints da API (app/main.py).

Utiliza o TestClient do FastAPI (síncrono) com monitor_price e
open_live_selector mockados, para evitar abertura de browsers.

Cobre:
- GET  /        → serve o HTML ou retorna 404 se template ausente
- POST /start   → inicia monitoramento, valida payload
- POST /stop    → encerra monitoramento, trata URL inexistente
- Validação de entrada via Pydantic (HTTP 422 para payload inválido)
"""

import pytest
import main  # importado no topo para garantir inicialização única do módulo


class TestIndexEndpoint:
    """Testa o endpoint raiz GET /."""

    def test_returns_html_or_404(self, client):
        """GET / deve retornar 200 (HTML) ou 404 se o template estiver ausente."""
        response = client.get("/")
        assert response.status_code in (200, 404)

    def test_200_has_html_content_type(self, client):
        """Se o template existir, o Content-Type deve ser text/html."""
        response = client.get("/")
        if response.status_code == 200:
            assert "text/html" in response.headers.get("content-type", "")


class TestStartEndpoint:
    """Testa o endpoint POST /start."""

    def test_valid_payload_returns_200(self, client):
        """Payload válido deve retornar HTTP 200."""
        response = client.post(
            "/start",
            json={"url": "http://example.com", "xpath": "div.price"},
        )
        assert response.status_code == 200

    def test_response_contains_message_key(self, client):
        """Corpo da resposta deve ter a chave 'message'."""
        response = client.post(
            "/start",
            json={"url": "http://example.com", "xpath": "#preco"},
        )
        assert "message" in response.json()

    def test_success_message_text(self, client):
        """Mensagem de sucesso deve informar que o monitoramento foi iniciado."""
        response = client.post(
            "/start",
            json={"url": "http://example.com", "xpath": "span.valor"},
        )
        data = response.json()
        assert "started" in data["message"].lower() or "iniciado" in data["message"].lower()

    def test_missing_xpath_returns_422(self, client):
        """Payload sem 'xpath' deve ser rejeitado com HTTP 422 (Unprocessable Entity)."""
        response = client.post("/start", json={"url": "http://example.com"})
        assert response.status_code == 422

    def test_missing_url_returns_422(self, client):
        """Payload sem 'url' deve ser rejeitado com HTTP 422."""
        response = client.post("/start", json={"xpath": "div"})
        assert response.status_code == 422

    def test_empty_body_returns_422(self, client):
        """Body vazio deve ser rejeitado com HTTP 422."""
        response = client.post("/start", json={})
        assert response.status_code == 422

    def test_duplicate_start_replaces_task(self, client):
        """Iniciar monitoramento da mesma URL duas vezes deve funcionar sem erro."""
        payload = {"url": "http://dup-test.com", "xpath": "span"}
        r1 = client.post("/start", json=payload)
        r2 = client.post("/start", json=payload)
        assert r1.status_code == 200
        assert r2.status_code == 200


class TestStopEndpoint:
    """Testa o endpoint POST /stop."""

    def test_stop_nonexistent_url_returns_200(self, client):
        """Parar URL não monitorada deve retornar 200 com mensagem informativa."""
        response = client.post("/stop", json={"url": "http://nao-existe.com"})
        assert response.status_code == 200

    def test_stop_nonexistent_url_message(self, client):
        """Mensagem para URL sem monitoramento ativo deve comunicar isso ao cliente."""
        response = client.post("/stop", json={"url": "http://nao-existe.com"})
        data = response.json()
        assert "No active monitoring" in data["message"] or "no active" in data["message"].lower()

    def test_stop_missing_url_returns_422(self, client):
        """Payload sem 'url' deve ser rejeitado com HTTP 422."""
        response = client.post("/stop", json={})
        assert response.status_code == 422

    def test_start_then_stop_lifecycle(self, client):
        """Iniciar e depois parar o monitoramento deve percorrer o ciclo completo."""
        url = "http://lifecycle-test.com"

        start_resp = client.post("/start", json={"url": url, "xpath": "h1"})
        assert start_resp.status_code == 200

        stop_resp = client.post("/stop", json={"url": url})
        assert stop_resp.status_code == 200
        stop_data = stop_resp.json()
        assert "stopped" in stop_data["message"].lower() or "encerrado" in stop_data["message"].lower()

    def test_stop_removes_task_from_active(self, client):
        """Após o stop, a URL não deve mais estar em active_tasks."""
        url = "http://remove-task-test.com"
        client.post("/start", json={"url": url, "xpath": "p"})
        client.post("/stop", json={"url": url})
        assert url not in main.active_tasks
