"""AgroVision AI — Router ETL."""
from __future__ import annotations

from fastapi import APIRouter, Query

from services.etl_service import build_dataset, get_enso_actual, get_enso_historico

router = APIRouter(prefix="/etl", tags=["ETL"])


@router.post("/build")
async def etl_build(max_eva: int = Query(10000, ge=1000, le=100000)):
    """Construye el dataset maestro completo (EVA + clima + ENSO)."""
    return await build_dataset(max_eva)


@router.get("/enso")
def enso_historico():
    """Índice ENSO histórico (ONI) 2007-2024."""
    return get_enso_historico()


@router.get("/enso/actual")
def enso_actual():
    """Fase ENSO del año en curso y su impacto esperado en Colombia."""
    return get_enso_actual()
