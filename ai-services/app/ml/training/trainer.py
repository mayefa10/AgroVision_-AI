"""AgroVision AI — Entrenamiento del modelo."""
from __future__ import annotations

import json
import logging
import os
import pickle
from datetime import datetime, timezone

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

from app.config.constants import ENCODERS_PATH, METRICS_PATH, MODEL_PATH
from app.infrastructure.clients.eva_client import EvaClient
from app.ml.features.engineering import FEATURE_COLS, prepare_features
from app.ml.features.selection import get_feature_importance
from app.ml.models.random_forest import AgroRandomForest

logger = logging.getLogger(__name__)


def _ensure_model_dir() -> None:
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)


def save_model(model: AgroRandomForest, encoders: dict) -> None:
    _ensure_model_dir()
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    with open(ENCODERS_PATH, "wb") as f:
        pickle.dump(encoders, f)
    logger.info("Modelo guardado en %s", MODEL_PATH)


def save_metrics(metrics: dict) -> None:
    """Persiste las métricas de entrenamiento en un JSON junto al modelo."""
    _ensure_model_dir()
    payload = {
        **metrics,
        "trained_at": datetime.now(timezone.utc).isoformat(),
    }
    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    logger.info("Métricas guardadas en %s", METRICS_PATH)


def load_metrics() -> dict | None:
    """Lee las métricas del último entrenamiento, si existen."""
    if not os.path.exists(METRICS_PATH):
        return None
    try:
        with open(METRICS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error("Error leyendo métricas: %s", e)
        return None


async def run_training(limit: int = 5000) -> dict:
    """
    Pipeline completo de entrenamiento:
    fetch EVA → preparar features → split → entrenar → evaluar → guardar.
    """
    logger.info("Iniciando entrenamiento con datos EVA (limit=%d)...", limit)

    # 1. Datos
    eva_client = EvaClient()
    df = await eva_client.fetch_paginated(limit=limit)

    if df.empty:
        return {"success": False, "message": "No se pudieron obtener datos EVA"}

    logger.info("EVA descargado: %d registros", len(df))

    # 2. Features
    X, y, encoders = prepare_features(df, fit=True)
    logger.info("Dataset listo para entrenamiento: %d filas, %d features", len(X), len(X.columns))

    if len(X) < 100:
        return {"success": False, "message": f"Insuficientes datos ({len(X)} filas)"}

    # 3. Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # 4. Entrenar
    model = AgroRandomForest()
    model.fit(X_train, y_train)

    # 5. Evaluar
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2  = r2_score(y_test, y_pred)

    # 6. Guardar modelo + métricas + limpiar cache del predictor
    save_model(model, encoders)
    importances = get_feature_importance(model.sklearn_model, FEATURE_COLS)

    metrics = {
        "success":                 True,
        "registros_entrenamiento": len(X_train),
        "registros_test":          len(X_test),
        "registros_totales":       len(X),
        "mae":                     round(mae, 3),
        "r2":                      round(r2, 3),
        "feature_importance":      importances,
        "model_path":              MODEL_PATH,
    }
    save_metrics(metrics)
    _invalidate_predictor_cache()

    logger.info("Entrenamiento completo — MAE: %.3f | R²: %.3f", mae, r2)

    return metrics


def _invalidate_predictor_cache() -> None:
    """Invalida el cache del predictor tras un nuevo entrenamiento."""
    try:
        from app.ml.inference.predictor import load_model_cached
        load_model_cached.cache_clear()
        logger.info("Cache del predictor invalidado")
    except Exception:
        pass