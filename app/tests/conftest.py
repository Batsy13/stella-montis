"""Shared configurations and fixtures for the test suite.

Fixtures defined here are automatically available to all test modules
via pytest without requiring explicit imports.
"""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Returns a FastAPI TestClient with mocked browser dependencies.

    The monitor_price and open_live_selector functions are replaced with
    AsyncMocks to prevent real Chromium instances from launching during tests.
    The active_tasks dictionary is cleared before and after each test to 
    ensure isolation between test cases.

    Yields:
        TestClient: An instance of the FastAPI test client.
    """
    with (
        patch("main.monitor_price", new_callable=AsyncMock),
        patch("main.open_live_selector", new_callable=AsyncMock),
    ):
        import main 

        main.active_tasks.clear()
        with TestClient(main.app) as test_client:
            yield test_client
        main.active_tasks.clear()