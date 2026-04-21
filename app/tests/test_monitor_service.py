"""
Testes unitários para services/monitor_service.py.

Foca na função send_google_form, que é pura (sem Playwright) e
totalmente testável via mock de requests.post.

Cobre:
- Chamada HTTP para a URL correta do Google Forms
- Envio do campo correto (entry.1608177186) com o valor passado
- Tratamento gracioso de erros de rede (sem crash)
- Casos de borda: mensagem vazia, mensagem multilinha
"""

import pytest
import requests
from unittest.mock import patch, MagicMock, call

from services.monitor_service import send_google_form

FORM_URL = (
    "https://docs.google.com/forms/d/e/"
    "1FAIpQLScYm5JlmnR1F2THqf00mKa3C71hgAVa2HLbIg84-88rw74ySw/formResponse"
)
FORM_ENTRY = "entry.1608177186"


class TestSendGoogleForm:
    """Testa o envio de notificações via Google Forms."""

    def test_calls_post_once(self):
        """Deve realizar exatamente uma chamada POST."""
        with patch("services.monitor_service.requests.post") as mock_post:
            send_google_form("mensagem de teste")
            assert mock_post.call_count == 1

    def test_calls_correct_url(self):
        """A URL de destino deve ser o endpoint de resposta do Google Forms."""
        with patch("services.monitor_service.requests.post") as mock_post:
            send_google_form("mensagem de teste")
            args, _ = mock_post.call_args
            assert args[0] == FORM_URL

    def test_sends_message_in_correct_field(self):
        """O campo entry.1608177186 deve conter exatamente o texto enviado."""
        with patch("services.monitor_service.requests.post") as mock_post:
            send_google_form("Valor alterado: R$ 100 -> R$ 200")
            _, kwargs = mock_post.call_args
            assert kwargs["data"][FORM_ENTRY] == "Valor alterado: R$ 100 -> R$ 200"

    def test_handles_generic_exception_without_raising(self):
        """Uma exceção genérica de rede não deve propagar (tratada internamente)."""
        with patch(
            "services.monitor_service.requests.post",
            side_effect=Exception("conexão recusada"),
        ):
            send_google_form("teste")  # não deve lançar

    def test_handles_connection_error_without_raising(self):
        """Um ConnectionError do requests não deve derrubar a aplicação."""
        with patch(
            "services.monitor_service.requests.post",
            side_effect=requests.exceptions.ConnectionError("timeout"),
        ):
            send_google_form("teste")  # não deve lançar

    def test_handles_timeout_without_raising(self):
        """Um Timeout do requests não deve derrubar a aplicação."""
        with patch(
            "services.monitor_service.requests.post",
            side_effect=requests.exceptions.Timeout("timeout"),
        ):
            send_google_form("teste")

    def test_empty_message_still_calls_post(self):
        """Mensagem vazia deve ser enviada normalmente (sem short-circuit)."""
        with patch("services.monitor_service.requests.post") as mock_post:
            send_google_form("")
            assert mock_post.call_count == 1
            _, kwargs = mock_post.call_args
            assert kwargs["data"][FORM_ENTRY] == ""

    def test_multiline_message_preserved(self):
        """Mensagem com quebras de linha deve chegar intacta ao formulário."""
        msg = "Valor alterado!\n\nURL: http://example.com\nAntigo: R$ 10\nNovo: R$ 20"
        with patch("services.monitor_service.requests.post") as mock_post:
            send_google_form(msg)
            _, kwargs = mock_post.call_args
            assert kwargs["data"][FORM_ENTRY] == msg

    def test_special_characters_in_message(self):
        """Caracteres especiais (acentos, símbolos) devem ser enviados sem erro."""
        msg = "Preço: R$ 1.234,56 — alterado às 14h30 (São Paulo)"
        with patch("services.monitor_service.requests.post") as mock_post:
            send_google_form(msg)
            _, kwargs = mock_post.call_args
            assert kwargs["data"][FORM_ENTRY] == msg
