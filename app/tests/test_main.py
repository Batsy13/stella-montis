"""Integration tests for API endpoints (app/main.py).

Uses FastAPI's TestClient (synchronous) with mocked monitor_price and
open_live_selector to avoid launching real browsers.

Covers:
- GET  /         → Serves HTML or returns 404 if template is missing.
- POST /start    → Initiates monitoring and validates payload.
- POST /stop     → Terminates monitoring and handles non-existent URLs.
- Input validation via Pydantic (HTTP 422 for invalid payloads).
"""

import main

class TestIndexEndpoint:
    """Tests the root GET / endpoint."""

    def test_returns_html_or_404(self, client):
        """GET / should return 200 (HTML) or 404 if the template is missing."""
        response = client.get("/")
        assert response.status_code in (200, 404)

    def test_200_has_html_content_type(self, client):
        """If the template exists, the Content-Type must be text/html."""
        response = client.get("/")
        if response.status_code == 200:
            assert "text/html" in response.headers.get("content-type", "")


class TestStartEndpoint:
    """Tests the POST /start endpoint."""

    def test_valid_payload_returns_200(self, client):
        """A valid payload should return HTTP 200."""
        response = client.post(
            "/start",
            json={"url": "http://example.com", "xpath": "div.price", "username": "tester"},
        )
        assert response.status_code == 200

    def test_response_contains_message_key(self, client):
        """The response body must contain a 'message' key."""
        response = client.post(
            "/start",
            json={"url": "http://example.com", "xpath": "#preco", "username": "tester"},
        )
        assert "message" in response.json()

    def test_success_message_text(self, client):
        """The success message should state that monitoring has started."""
        response = client.post(
            "/start",
            json={"url": "http://example.com", "xpath": "span.valor", "username": "tester"},
        )
        data = response.json()
        message = data["message"].lower()
        assert "started" in message or "iniciado" in message

    def test_missing_xpath_returns_422(self, client):
        """Payload without 'xpath' should be rejected with HTTP 422 (Unprocessable Entity)."""
        response = client.post("/start", json={"url": "http://example.com", "username": "tester"})
        assert response.status_code == 422

    def test_missing_url_returns_422(self, client):
        """Payload without 'url' should be rejected with HTTP 422."""
        response = client.post("/start", json={"xpath": "div", "username": "tester"})
        assert response.status_code == 422

    def test_empty_body_returns_422(self, client):
        """An empty body should be rejected with HTTP 422."""
        response = client.post("/start", json={})
        assert response.status_code == 422

    def test_duplicate_start_replaces_task(self, client):
        """Starting monitoring for the same URL twice should work without error."""
        payload = {"url": "http://dup-test.com", "xpath": "span", "username": "tester"}
        r1 = client.post("/start", json=payload)
        r2 = client.post("/start", json=payload)
        assert r1.status_code == 200
        assert r2.status_code == 200


class TestStopEndpoint:
    """Tests the POST /stop endpoint."""

    def test_stop_nonexistent_url_returns_200(self, client):
        """Stopping an unmonitored URL should return 200 with an informative message."""
        response = client.post("/stop", json={"url": "http://nao-existe.com", "username": "tester"})
        assert response.status_code == 200

    def test_stop_nonexistent_url_message(self, client):
        """The message for a URL without active monitoring should inform the client."""
        response = client.post("/stop", json={"url": "http://nao-existe.com", "username": "tester"})
        data = response.json()
        message = data["message"].lower()
        assert "no active monitoring" in message or "no active" in message

    def test_stop_missing_url_returns_422(self, client):
        """Payload without 'url' should be rejected with HTTP 422."""
        response = client.post("/stop", json={})
        assert response.status_code == 422

    def test_start_then_stop_lifecycle(self, client):
        """Starting and then stopping monitoring should complete the full lifecycle."""
        url = "http://lifecycle-test.com"

        start_resp = client.post("/start", json={"url": url, "xpath": "h1", "username": "tester"})
        assert start_resp.status_code == 200

        stop_resp = client.post("/stop", json={"url": url, "username": "tester"})
        assert stop_resp.status_code == 200
        stop_data = stop_resp.json()
        message = stop_data["message"].lower()
        assert "stopped" in message or "encerrado" in message

    def test_stop_removes_task_from_active(self, client):
        """After a stop request, the URL should no longer be in active_tasks."""
        url = "http://remove-task-test.com"
        client.post("/start", json={"url": url, "xpath": "p", "username": "tester"})
        client.post("/stop", json={"url": url, "username": "tester"})
        assert url not in main.active_tasks