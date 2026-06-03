"""Tests unitarios — EvaClient."""
from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pandas as pd
import pytest

from app.infrastructure.clients.eva_client import EvaClient


@pytest.fixture
def client() -> EvaClient:
    return EvaClient()


@pytest.mark.asyncio
async def test_fetch_retorna_success_con_datos(client, mock_eva_response):
    with patch.object(client, "get_safe", AsyncMock(return_value=mock_eva_response)):
        result = await client.fetch(departamento="ANTIOQUIA")

    assert result["success"] is True
    assert result["total_registros"] == len(mock_eva_response)
    assert "estadisticas" in result


@pytest.mark.asyncio
async def test_fetch_retorna_failure_sin_datos(client):
    with patch.object(client, "get_safe", AsyncMock(return_value=[])):
        result = await client.fetch()

    assert result["success"] is False
    assert "data" in result


@pytest.mark.asyncio
async def test_fetch_paginated_retorna_dataframe(client, mock_eva_response):
    with patch.object(client, "get_safe", AsyncMock(side_effect=[mock_eva_response, []])):
        df = await client.fetch_paginated(limit=1000)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == len(mock_eva_response)


@pytest.mark.asyncio
async def test_fetch_calcula_estadisticas(client, mock_eva_response):
    with patch.object(client, "get_safe", AsyncMock(return_value=mock_eva_response)):
        result = await client.fetch()

    stats = result["estadisticas"]
    assert "rendimiento_promedio" in stats
    assert stats["rendimiento_promedio"] > 0
