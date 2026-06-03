"""AgroVision AI — Configuración global de pytest."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def mock_eva_response() -> list[dict]:
    return json.loads((FIXTURES_DIR / "mock_eva_response.json").read_text())


@pytest.fixture
def mock_nasa_response() -> dict:
    return json.loads((FIXTURES_DIR / "mock_nasa_response.json").read_text())


@pytest.fixture
def sample_clima_stats() -> dict:
    """Estadísticas climáticas de muestra para tests de alertas."""
    return {
        "temperatura_promedio":   22.5,
        "temperatura_max":        28.0,
        "temperatura_min":        14.0,
        "precipitacion_promedio": 3.0,
        "precipitacion_total":    21.0,
        "humedad_promedio":       35.0,
        "dias_sin_lluvia":        8,
        "dias_con_lluvia":        6,
    }


@pytest.fixture
def sample_clima_inundacion() -> dict:
    return {
        "temperatura_promedio":   25.0,
        "temperatura_max":        29.0,
        "temperatura_min":        20.0,
        "precipitacion_promedio": 75.0,
        "precipitacion_total":    525.0,
        "humedad_promedio":       92.0,
        "dias_sin_lluvia":        0,
        "dias_con_lluvia":        7,
    }
