# ── OpenWeather Router ────────────────────────────────────
"""AgroVision AI — Router OpenWeather."""
from __future__ import annotations

import asyncio

from fastapi import APIRouter

from app.config.constants import DEPARTAMENTOS
from app.infrastructure.clients.weather_client import WeatherClient

openweather_router = APIRouter(prefix="/openweather", tags=["OpenWeather"])

_weather = WeatherClient()


@openweather_router.get("/{departamento}")
async def clima_actual_depto(departamento: str):
    """Condiciones actuales OpenWeather para la capital de un departamento."""
    info = DEPARTAMENTOS.get(departamento.upper())
    if not info:
        return {"success": False, "message": f"Departamento '{departamento}' no encontrado"}
    return await _weather.fetch_current(info["capital"], departamento.upper())


@openweather_router.get("")
async def clima_actual_todos():
    """Condiciones actuales para todas las capitales departamentales."""
    semaphore = asyncio.Semaphore(5)

    async def one(name: str, info: dict) -> dict:
        async with semaphore:
            result = await _weather.fetch_current(info["capital"], name)
            return {"departamento": name, **result}

    results = await asyncio.gather(
        *[one(n, i) for n, i in DEPARTAMENTOS.items()],
        return_exceptions=True,
    )
    successful = [r for r in results if isinstance(r, dict) and r.get("success")]
    return {"success": True, "total": len(successful), "data": successful}