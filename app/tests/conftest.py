"""
Configurações e fixtures compartilhadas para a suite de testes.

Fixtures definidas aqui ficam disponíveis para todos os módulos de teste
automaticamente pelo pytest (sem necessidade de import explícito).
"""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """
    Retorna um TestClient do FastAPI com as dependências de browser mockadas.

    O monitor_price e o open_live_selector são substituídos por AsyncMocks
    para que nenhum browser Chromium real seja aberto durante os testes.
    O dicionário active_tasks é limpo antes e depois de cada teste para
    garantir isolamento entre os casos.
    """
    with (
        patch("main.monitor_price", new_callable=AsyncMock),
        patch("main.open_live_selector", new_callable=AsyncMock),
    ):
        import main  # noqa: PLC0415 — importado aqui para capturar os patches

        main.active_tasks.clear()
        with TestClient(main.app) as test_client:
            yield test_client
        main.active_tasks.clear()
