"""AgroVision AI — Servicio ML (fachada)."""
from __future__ import annotations

from app.ml.inference.predictor import model_is_trained, predict_rendimiento
from app.ml.training.trainer import run_training


async def train() -> dict:
    return await run_training()


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
    return {
        "model_trained": trained,
        "message": "Listo para predecir" if trained else "Llama a POST /ml/train primero",
    }
