"""AgroVision AI — Router DANE / DIVIPOLA."""
from __future__ import annotations

import asyncio
from typing import Optional

from fastapi import APIRouter, Query

from app.infrastructure.clients.dane_client import DaneClient

router = APIRouter(prefix="/dane", tags=["DANE"])

_dane = DaneClient()


@router.get("/municipios")
async def municipios(departamento: Optional[str] = Query(None)):
    """Municipios con coordenadas (geo + códigos fusionados)."""
    geo_task, cod_task = await asyncio.gather(
        _dane.fetch_geo(departamento),
        _dane.fetch_codigos(departamento),
    )
    # Prioriza datos geo; fallback a códigos
    data = geo_task.get("data") or cod_task.get("data", [])
    return {
        "success":          True,
        "source":           "DANE — DIVIPOLA",
        "total_municipios": len(data),
        "departamento":     departamento,
        "data":             data,
    }


@router.get("/lookup/{nombre}")
async def lookup_municipio(nombre: str):
    """Busca un municipio por nombre y retorna código DANE y coordenadas."""
    return await _dane.lookup(nombre)


@router.get("/geo")
async def geo(departamento: Optional[str] = Query(None)):
    """DIVIPOLA con coordenadas geográficas."""
    return await _dane.fetch_geo(departamento)


@router.get("/codigos")
async def codigos(
    departamento:     Optional[str] = Query(None),
    codigo_municipio: Optional[str] = Query(None),
):
    """Códigos DANE oficiales DIVIPOLA."""
    return await _dane.fetch_codigos(departamento, codigo_municipio)
