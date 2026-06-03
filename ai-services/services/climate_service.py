"""AgroVision AI — Servicio de clima (NASA + OpenWeather)."""
from __future__ import annotations

import asyncio
import logging
from typing import Optional

from app.config.constants import DEPARTAMENTOS
from app.infrastructure.clients.nasa_client import NasaClient
from app.infrastructure.clients.weather_client import WeatherClient

logger = logging.getLogger(__name__)

_nasa    = NasaClient()
_weather = WeatherClient()


async def get_clima_departamento(departamento: str, days: int = 30) -> dict:
    info = DEPARTAMENTOS.get(departamento.upper())
    if not info:
        return {"success": False, "message": f"Departamento '{departamento}' no disponible"}
    return await _nasa.fetch_daily(info["lat"], info["lng"], days, departamento.upper())


async def get_clima_todos(days: int = 30) -> dict:
    semaphore = asyncio.Semaphore(5)

    async def one(name: str, info: dict) -> dict:
        async with semaphore:
            result = await _nasa.fetch_daily(info["lat"], info["lng"], days, name)
            return {"departamento": name, **result}

    results = await asyncio.gather(
        *[one(n, i) for n, i in DEPARTAMENTOS.items()],
        return_exceptions=True,
    )
    successful = [r for r in results if isinstance(r, dict) and r.get("success")]
    return {
        "success":               True,
        "total_departamentos":   len(successful),
        "data":                  successful,
    }


async def get_clima_actual(ciudad: str, departamento: Optional[str] = None) -> dict:
    return await _weather.fetch_current(ciudad, departamento)


async def get_clima_actual_todos() -> dict:
    tasks = [
        _weather.fetch_current(info["capital"], name)
        for name, info in DEPARTAMENTOS.items()
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    successful = [r for r in results if isinstance(r, dict) and r.get("success")]
    return {"success": True, "total": len(successful), "data": successful}
