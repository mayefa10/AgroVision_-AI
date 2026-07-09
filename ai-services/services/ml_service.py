"""AgroVision AI — Servicio ML (fachada)."""
# Copyright (C) 2026 July Mayerly Quintero Farfán

from __future__ import annotations

from app.ml.inference.predictor import model_is_trained, predict_rendimiento
from app.ml.training.trainer import load_metrics, run_training


async def train() -> dict:
    return await run_training(limit=20000)


def predict(
    departamento: str,
    cultivo: str,
    grupo_cultivo: str,
    area_sembrada: float,
    anio: int,
    periodo: int = 0,
) -> dict:
    return predict_rendimiento(departamento, cultivo, grupo_cultivo, area_sembrada, anio, periodo)


def status() -> dict:
    trained = model_is_trained()
    metrics = load_metrics() if trained else None

    return {
        "model_trained": trained,
        "message": "Listo para predecir" if trained else "Llama a POST /ml/train primero",
        # Incluye un resumen de métricas directamente en /ml/status
        # para que el frontend no necesite dos llamadas.
        "metrics": metrics,
    }


def metrics() -> dict:
    """Métricas detalladas del último entrenamiento."""
    data = load_metrics()
    if data is None:
        return {
            "success": False,
            "message": "El modelo no ha sido entrenado todavía. Llama a POST /ml/train.",
        }
    return data