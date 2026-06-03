"""AgroVision AI — Router EVA (Evaluaciones Agropecuarias)."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Query

from services.eva_service import get_eva, get_eva_summary

router = APIRouter(prefix="/eva", tags=["EVA"])


@router.get("/summary")
async def eva_summary():
    """Resumen nacional EVA: top cultivos y departamentos por producción."""
    return await get_eva_summary()


@router.get("")
async def eva_data(
    departamento: Optional[str] = Query(None),
    cultivo:      Optional[str] = Query(None),
    anio:         Optional[int] = Query(None),
    limit:        int           = Query(1000, ge=1, le=5000),
):
    """Consulta datos EVA con filtros opcionales."""
    return await get_eva(departamento, cultivo, anio, limit)
