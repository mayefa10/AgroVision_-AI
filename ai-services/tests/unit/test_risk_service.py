"""Tests unitarios — risk_service."""
from __future__ import annotations

import pytest

from app.domain.enums import PredictionType, RiskLevel
from app.domain.schemas import PredictRiskRequest
from services.risk_service import calculate_risk


def _req(**kwargs) -> PredictRiskRequest:
    defaults = dict(
        region_code="05001",
        prediction_type=PredictionType.SEQUIA,
        temperatura=25.0,
        humedad=60.0,
        precipitacion=10.0,
    )
    defaults.update(kwargs)
    return PredictRiskRequest(**defaults)


class TestSequia:
    def test_condiciones_normales_da_low(self):
        level, conf = calculate_risk(_req(precipitacion=20, humedad=70, temperatura=25))
        assert level == RiskLevel.LOW

    def test_precipitacion_baja_eleva_riesgo(self):
        level, _ = calculate_risk(_req(precipitacion=2, humedad=30, temperatura=34))
        assert level in {RiskLevel.HIGH, RiskLevel.CRITICAL}

    def test_confidence_en_rango(self):
        _, conf = calculate_risk(_req())
        assert 0.60 <= conf <= 0.95


class TestInundacion:
    def test_lluvia_extrema_da_critical(self):
        req = _req(
            prediction_type=PredictionType.INUNDACION,
            precipitacion=90,
            humedad=95,
            temperatura=26,
        )
        level, _ = calculate_risk(req)
        assert level in {RiskLevel.HIGH, RiskLevel.CRITICAL}

    def test_lluvia_normal_da_low(self):
        req = _req(
            prediction_type=PredictionType.INUNDACION,
            precipitacion=10,
            humedad=60,
            temperatura=25,
        )
        level, _ = calculate_risk(req)
        assert level == RiskLevel.LOW


class TestHelada:
    def test_temperatura_critica(self):
        req = _req(
            prediction_type=PredictionType.HELADA,
            temperatura=2,
            humedad=50,
            precipitacion=5,
            altitud=3000,
        )
        level, _ = calculate_risk(req)
        assert level in {RiskLevel.HIGH, RiskLevel.CRITICAL}

    def test_temperatura_normal_da_low(self):
        req = _req(
            prediction_type=PredictionType.HELADA,
            temperatura=20,
            humedad=60,
            precipitacion=10,
        )
        level, _ = calculate_risk(req)
        assert level == RiskLevel.LOW
