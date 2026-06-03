"""Tests de integración — NasaClient."""
from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.infrastructure.clients.nasa_client import NasaClient


@pytest.fixture
def nasa() -> NasaClient:
    return NasaClient()


@pytest.mark.asyncio
async def test_fetch_daily_estructura(nasa, mock_nasa_response):
    with patch.object(nasa, "get_safe", AsyncMock(return_value=mock_nasa_response)):
        result = await nasa.fetch_daily(lat=6.2442, lng=-75.5812, days=7, departamento="ANTIOQUIA")

    assert result["success"] is True
    assert "estadisticas" in result
    assert "data" in result
    stats = result["estadisticas"]
    assert stats["temperatura_promedio"] > 0
    assert stats["dias_sin_lluvia"] >= 0
    assert stats["dias_con_lluvia"] >= 0


@pytest.mark.asyncio
async def test_fetch_daily_falla_gracefully(nasa):
    with patch.object(nasa, "get_safe", AsyncMock(return_value={})):
        result = await nasa.fetch_daily(lat=6.2442, lng=-75.5812, days=7)

    assert result["success"] is False


@pytest.mark.asyncio
async def test_fetch_annual_estructura(nasa, mock_nasa_response):
    # Adaptar fixture a formato anual
    annual_response = {
        "properties": {
            "parameter": {
                "T2M":            {"2023": 23.5},
                "PRECTOTCORR":    {"2023": 4.2},
                "RH2M":           {"2023": 70.0},
                "ALLSKY_SFC_SW_DWN": {"2023": 18.5},
            }
        }
    }
    with patch.object(nasa, "get_safe", AsyncMock(return_value=annual_response)):
        result = await nasa.fetch_annual(lat=6.2442, lng=-75.5812, anio=2023, departamento="ANTIOQUIA")

    assert result["anio"] == 2023
    assert result["temp_promedio"] == 23.5
    assert result["precipitacion"] == 4.2
