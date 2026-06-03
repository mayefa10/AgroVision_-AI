"""AgroVision AI — Router clima."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Query

from app.config.constants import DEPARTAMENTOS
from services.climate_service import (
    get_clima_actual,
    get_clima_actual_todos,
    get_clima_departamento,
    get_clima_todos,
)
from services.eva_service import get_full_pipeline

router = APIRouter(prefix="", tags=["Clima"])


@router.get("/departamentos")
def listar_departamentos():
    """Lista todos los departamentos con coordenadas y capital."""
    return {
        "total": len(DEPARTAMENTOS),
        "departamentos": [
            {"nombre": k, "capital": v["capital"], "lat": v["lat"], "lng": v["lng"], "codigo": v["codigo"]}
            for k, v in DEPARTAMENTOS.items()
        ],
    }


@router.get("/clima/{departamento}")
async def clima_departamento(departamento: str, days: int = Query(30, ge=1, le=90)):
    """Datos climáticos NASA POWER para un departamento (últimos N días)."""
    return await get_clima_departamento(departamento, days)


@router.get("/clima")
async def clima_todos(days: int = Query(30, ge=1, le=90)):
    """Datos climáticos para todos los departamentos en paralelo."""
    return await get_clima_todos(days)


@router.get("/clima-actual/{ciudad}")
async def clima_actual(ciudad: str, departamento: Optional[str] = Query(None)):
    """Condiciones actuales OpenWeather para una ciudad."""
    return await get_clima_actual(ciudad, departamento)


@router.get("/clima-actual")
async def clima_actual_todos():
    """Condiciones actuales para todas las capitales departamentales."""
    return await get_clima_actual_todos()


@router.get("/pipeline/{departamento}")
async def pipeline_completo(
    departamento: str,
    cultivo: str = Query("MAIZ"),
):
    """Pipeline completo EVA + NASA + OpenWeather para un departamento."""
    return await get_full_pipeline(departamento.upper(), cultivo.upper())
