"""
AgroVision AI — Routers nuevos:
  /enso/*         → Monitor ENSO (datos NOAA reales)
  /openweather/*  → Clima actual OpenWeather
  /escenarios/*   → Escenarios IA (El Niño / La Niña)
"""
from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, Query

# ── ENSO Router ───────────────────────────────────────────

enso_router = APIRouter(prefix="/enso", tags=["ENSO"])


@enso_router.get("")
async def enso_actual():
    """Estado ENSO actual con índice ONI real de NOAA/CPC."""
    from app.infrastructure.clients.noaa_client import noaa_client
    return await noaa_client.fetch_enso_actual()


@enso_router.get("/historico")
async def enso_historico(anios: int = Query(5, ge=1, le=20)):
    """Serie histórica ONI de los últimos N años."""
    from app.infrastructure.clients.noaa_client import noaa_client
    return await noaa_client.fetch_oni_historico(anios=anios)


@enso_router.get("/escenarios")
async def escenarios_enso(
    departamento: str = Query("ANTIOQUIA"),
    cultivo:      str = Query("MAIZ"),
):
    """Escenarios de impacto agrícola El Niño / La Niña para un departamento."""
    from app.infrastructure.clients.noaa_client import noaa_client
    return await noaa_client.fetch_escenarios(
        departamento=departamento.upper(),
        cultivo=cultivo.upper(),
    )
