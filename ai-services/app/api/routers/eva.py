"""AgroVision AI — Router EVA (Evaluaciones Agropecuarias)."""
from __future__ import annotations

from typing import Optional

import httpx
from fastapi import APIRouter, Query

from app.config.constants import EVA_2019_2024, SOCRATA_BASE
from app.infrastructure.persistence.postgres_client import get_or_fetch
from services.eva_service import get_eva, get_eva_summary

router = APIRouter(prefix="/eva", tags=["EVA"])


# ── Departamentos dinámicos ───────────────────────────────

@router.get("/departamentos")
async def eva_departamentos():
    """
    Lista de departamentos con datos reales en el dataset EVA.
    Se cachea 24h en PostgreSQL — solo consulta la API externa
    la primera vez o cuando el cache expira.
    """
    return await get_or_fetch(
        cache_key="eva:departamentos:lista",
        source="eva",
        category="AGRICULTURA",
        fetch_fn=_fetch_departamentos_real,
    )


async def _fetch_departamentos_real() -> dict:
    """Consulta Socrata agrupando por departamento para obtener la lista real."""
    url = f"{SOCRATA_BASE}/{EVA_2019_2024}.json"
    params = {
        "$select": "upper(departamento) as departamento, count(*) as total",
        "$group":  "upper(departamento)",
        "$where":  "rendimiento IS NOT NULL AND rendimiento > 0",
        "$order":  "upper(departamento) ASC",
        "$limit":  "100",
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.get(url, params=params)
            r.raise_for_status()
            data = r.json()
    except Exception as e:
        return {"success": False, "message": str(e), "departamentos": []}

    departamentos = [
        {
            "nombre":          row["departamento"],
            "total_registros": int(row.get("total", 0)),
        }
        for row in data
        if row.get("departamento")
    ]

    return {
        "success":       True,
        "departamentos": departamentos,
        "total":         len(departamentos),
        "source":        "EVA — datos.gov.co",
    }


# ── Endpoints existentes ──────────────────────────────────

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