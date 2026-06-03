"""AgroVision AI — Servicio EVA."""
from __future__ import annotations

import asyncio
from typing import Optional

from app.config.constants import DEPARTAMENTOS
from app.infrastructure.clients.eva_client import EvaClient
from app.infrastructure.clients.nasa_client import NasaClient
from app.infrastructure.clients.weather_client import WeatherClient

_eva     = EvaClient()
_nasa    = NasaClient()
_weather = WeatherClient()


async def get_eva(
    departamento: Optional[str] = None,
    cultivo: Optional[str] = None,
    anio: Optional[int] = None,
    limit: int = 1000,
) -> dict:
    return await _eva.fetch(departamento, cultivo, anio, limit)


async def get_eva_summary() -> dict:
    return await _eva.fetch_summary()


async def get_full_pipeline(departamento: str, cultivo: str = "MAIZ") -> dict:
    """EVA + NASA + OpenWeather para un departamento en paralelo."""
    info = DEPARTAMENTOS.get(departamento.upper(), {
        "lat": 4.7110, "lng": -74.0721, "capital": "Bogota",
    })
    from app.utils.dates import utcnow_iso
    eva_data, nasa_data, weather_data = await asyncio.gather(
        _eva.fetch(departamento=departamento, cultivo=cultivo),
        _nasa.fetch_daily(info["lat"], info["lng"], departamento=departamento),
        _weather.fetch_current(info["capital"], departamento),
    )
    return {
        "departamento":    departamento.upper(),
        "cultivo":         cultivo.upper(),
        "eva":             eva_data,
        "clima_historico": nasa_data,
        "clima_actual":    weather_data,
        "pipeline_at":     utcnow_iso(),
    }
