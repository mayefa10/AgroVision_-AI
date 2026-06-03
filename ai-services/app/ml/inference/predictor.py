"""AgroVision AI — Inferencia del modelo (predictor)."""
from __future__ import annotations

import logging
import os
import pickle
from functools import lru_cache
from typing import Optional

import pandas as pd

from app.config.constants import ENCODERS_PATH, MODEL_PATH
from app.domain.enums import YieldLevel
from app.domain.models import YieldPrediction
from app.ml.features.engineering import prepare_features
from app.ml.models.random_forest import AgroRandomForest

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def load_model_cached() -> tuple[Optional[AgroRandomForest], Optional[dict]]:
    """
    Carga modelo y encoders desde disco UNA sola vez.
    lru_cache garantiza que requests posteriores no toquen disco.
    Se invalida llamando a load_model_cached.cache_clear().
    """
    if not os.path.exists(MODEL_PATH):
        logger.warning("Modelo no encontrado en %s", MODEL_PATH)
        return None, None
    try:
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)
        with open(ENCODERS_PATH, "rb") as f:
            encoders = pickle.load(f)
        logger.info("Modelo cargado desde %s", MODEL_PATH)
        return model, encoders
    except Exception as e:
        logger.error("Error cargando modelo: %s", e)
        return None, None


def _classify_yield(pred: float) -> YieldLevel:
    if pred > 15:
        return YieldLevel.EXCELENTE
    if pred > 8:
        return YieldLevel.BUENO
    if pred > 4:
        return YieldLevel.REGULAR
    return YieldLevel.BAJO


def predict_rendimiento(
    departamento: str,
    cultivo: str,
    grupo_cultivo: str,
    area_sembrada: float,
    anio: int,
    periodo: int = 0,
) -> dict:
    """
    Predice rendimiento (t/ha) para un cultivo/región.
    Retorna dict compatible con RendimientoResponse.
    """
    model, encoders = load_model_cached()

    if model is None:
        return {
            "success": False,
            "message": "Modelo no entrenado. Llama a POST /ml/train primero.",
        }

    input_df = pd.DataFrame([{
        "departamento":  departamento.upper(),
        "cultivo":       cultivo.upper(),
        "grupo_cultivo": grupo_cultivo.upper(),
        "area_sembrada": area_sembrada,
        "anio":          anio,
        "periodo_num":   periodo,
    }])

    X, _, _ = prepare_features(input_df, encoders=encoders, fit=False)
    prediction = float(model.predict(X)[0])
    nivel = _classify_yield(prediction)

    return {
        "success":              True,
        "departamento":         departamento,
        "cultivo":              cultivo,
        "rendimiento_predicho": round(prediction, 2),
        "unidad":               "t/ha",
        "nivel":                nivel.value,
        "anio":                 anio,
        "area_sembrada":        area_sembrada,
    }


def model_is_trained() -> bool:
    return os.path.exists(MODEL_PATH) and os.path.exists(ENCODERS_PATH)
