"""AgroVision AI — Servicio NASA POWER (acceso directo para ETL)."""
# Copyright (C) 2026 July Mayerly Quintero Farfán

from __future__ import annotations

from typing import Optional

from app.infrastructure.clients.nasa_client import NasaClient

_nasa = NasaClient()


async def fetch_daily(lat: float, lng: float, days: int = 30, departamento: Optional[str] = None) -> dict:
    return await _nasa.fetch_daily(lat, lng, days, departamento)


async def fetch_annual(lat: float, lng: float, anio: int, departamento: Optional[str] = None) -> dict:
    return await _nasa.fetch_annual(lat, lng, anio, departamento)
