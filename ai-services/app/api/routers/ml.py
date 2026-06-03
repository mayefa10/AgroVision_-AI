"""AgroVision AI — Router ML."""
from __future__ import annotations

from fastapi import APIRouter

from app.domain.schemas import RendimientoRequest
from services.ml_service import predict, status, train

router = APIRouter(prefix="/ml", tags=["ML"])


@router.get("/status")
def ml_status():
    """Estado del modelo: entrenado o pendiente."""
    return status()


@router.post("/train")
async def ml_train():
    """Entrena el modelo Random Forest con datos EVA reales."""
    return await train()


@router.post("/predict-rendimiento")
def ml_predict(req: RendimientoRequest):
    """Predice el rendimiento (t/ha) para un cultivo en una región."""
    return predict(
        req.departamento,
        req.cultivo,
        req.grupo_cultivo,
        req.area_sembrada,
        req.anio,
        req.periodo,
    )
