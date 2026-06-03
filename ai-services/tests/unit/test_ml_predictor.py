"""Tests unitarios — predictor ML."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

from app.ml.features.engineering import prepare_features
from app.ml.inference.predictor import _classify_yield, model_is_trained, predict_rendimiento
from app.domain.enums import YieldLevel


# ── prepare_features ──────────────────────────────────────

def test_prepare_features_fit_retorna_correctamente(mock_eva_response):
    df = pd.DataFrame(mock_eva_response).rename(columns={
        "a_o": "anio", "rea_sembrada": "area_sembrada"
    })
    X, y, encoders = prepare_features(df, fit=True)
    assert not X.empty
    assert y is not None
    assert "departamento" in encoders


def test_prepare_features_inference_sin_modelo(mock_eva_response):
    df = pd.DataFrame(mock_eva_response).rename(columns={
        "a_o": "anio", "rea_sembrada": "area_sembrada"
    })
    _, _, encoders = prepare_features(df, fit=True)

    input_df = pd.DataFrame([{
        "departamento": "ANTIOQUIA", "cultivo": "MAIZ",
        "grupo_cultivo": "CEREALES Y LEGUMINOSAS",
        "area_sembrada": 100.0, "anio": 2024, "periodo_num": 1,
    }])
    X_inf, _, _ = prepare_features(input_df, encoders=encoders, fit=False)
    assert len(X_inf) == 1


def test_prepare_features_categoria_desconocida(mock_eva_response):
    df = pd.DataFrame(mock_eva_response).rename(columns={
        "a_o": "anio", "rea_sembrada": "area_sembrada"
    })
    _, _, encoders = prepare_features(df, fit=True)

    input_df = pd.DataFrame([{
        "departamento": "DEPARTAMENTO_NUEVO", "cultivo": "CULTIVO_NUEVO",
        "grupo_cultivo": "GRUPO_NUEVO",
        "area_sembrada": 50.0, "anio": 2024, "periodo_num": 0,
    }])
    # No debe lanzar excepción
    X_inf, _, _ = prepare_features(input_df, encoders=encoders, fit=False)
    assert len(X_inf) == 1


# ── clasificación de rendimiento ──────────────────────────

@pytest.mark.parametrize("pred,expected", [
    (20.0, YieldLevel.EXCELENTE),
    (10.0, YieldLevel.BUENO),
    (5.0,  YieldLevel.REGULAR),
    (1.0,  YieldLevel.BAJO),
])
def test_classify_yield(pred, expected):
    assert _classify_yield(pred) == expected


# ── predict_rendimiento sin modelo ────────────────────────

def test_predict_sin_modelo_retorna_error():
    with patch("app.ml.inference.predictor.load_model_cached", return_value=(None, None)):
        result = predict_rendimiento("ANTIOQUIA", "MAIZ", "CEREALES", 100.0, 2024)
    assert result["success"] is False
    assert "train" in result["message"].lower()


def test_predict_con_modelo_retorna_resultado(mock_eva_response):
    df = pd.DataFrame(mock_eva_response).rename(columns={
        "a_o": "anio", "rea_sembrada": "area_sembrada"
    })
    _, _, encoders = prepare_features(df, fit=True)

    mock_model = MagicMock()
    mock_model.predict.return_value = np.array([6.5])

    with patch("app.ml.inference.predictor.load_model_cached", return_value=(mock_model, encoders)):
        result = predict_rendimiento("ANTIOQUIA", "MAIZ", "CEREALES Y LEGUMINOSAS", 100.0, 2024)

    assert result["success"] is True
    assert result["rendimiento_predicho"] == 6.5
    assert result["nivel"] == YieldLevel.REGULAR.value
