"""Unit tests for services/monitor_service.py.

Focuses on the send_google_form function, which is a pure function (no Playwright)
and fully testable via requests.post mocking.

Covers:
- HTTP calls to the correct Google Forms URL.
- Submission of the correct field (entry.1608177186) with the provided value.
- Graceful handling of network errors (no crashes).
- Edge cases: empty messages, multiline messages.
"""

import requests
from unittest.mock import patch

from services.monitor_service import send_google_form

FORM_URL = (
    "https://docs.google.com/forms/d/e/"
    "1FAIpQLScYm5JlmnR1F2THqf00mKa3C71hgAVa2HLbIg84-88rw74ySw/formResponse"
)
FORM_ENTRY = "entry.1608177186"


class TestSendGoogleForm:
    """Tests notification delivery via Google Forms."""

    def test_calls_post_once(self):
        """Should perform exactly one POST call."""
        with patch("services.monitor_service.requests.post") as mock_post:
            send_google_form("test message")
            assert mock_post.call_count == 1

    def test_calls_correct_url(self):
        """The target URL must be the Google Forms response endpoint."""
        with patch("services.monitor_service.requests.post") as mock_post:
            send_google_form("test message")
            args, _ = mock_post.call_args
            assert args[0] == FORM_URL

    def test_sends_message_in_correct_field(self):
        """The entry.1608177186 field must contain exactly the sent text."""
        with patch("services.monitor_service.requests.post") as mock_post:
            message = "Price changed: R$ 100 -> R$ 200"
            send_google_form(message)
            _, kwargs = mock_post.call_args
            assert kwargs["data"][FORM_ENTRY] == message

    def test_handles_generic_exception_without_raising(self):
        """A generic network exception should not propagate (handled internally)."""
        with patch(
            "services.monitor_service.requests.post",
            side_effect=Exception("connection refused"),
        ):
            send_google_form("test")  # Should not raise

    def test_handles_connection_error_without_raising(self):
        """A requests ConnectionError should not crash the application."""
        with patch(
            "services.monitor_service.requests.post",
            side_effect=requests.exceptions.ConnectionError("timeout"),
        ):
            send_google_form("test")  # Should not raise

    def test_handles_timeout_without_raising(self):
        """A requests Timeout should not crash the application."""
        with patch(
            "services.monitor_service.requests.post",
            side_effect=requests.exceptions.Timeout("timeout"),
        ):
            send_google_form("test")

    def test_empty_message_still_calls_post(self):
        """An empty message should be sent normally without short-circuiting."""
        with patch("services.monitor_service.requests.post") as mock_post:
            send_google_form("")
            assert mock_post.call_count == 1
            _, kwargs = mock_post.call_args
            assert kwargs["data"][FORM_ENTRY] == ""

    def test_multiline_message_preserved(self):
        """Messages with line breaks should arrive intact at the form."""
        msg = "Price changed!\n\nURL: http://example.com\nOld: R$ 10\nNew: R$ 20"
        with patch("services.monitor_service.requests.post") as mock_post:
            send_google_form(msg)
            _, kwargs = mock_post.call_args
            assert kwargs["data"][FORM_ENTRY] == msg

    def test_special_characters_in_message(self):
        """Special characters (accents, symbols) should be sent without error."""
        msg = "Preço: R$ 1.234,56 — alterado às 14h30 (São Paulo)"
        with patch("services.monitor_service.requests.post") as mock_post:
            send_google_form(msg)
            _, kwargs = mock_post.call_args
            assert kwargs["data"][FORM_ENTRY] == msg