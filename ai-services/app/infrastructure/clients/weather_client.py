"""AgroVision AI — Cliente OpenWeather."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

from app.config.constants import OPENWEATHER_URL
from app.config.settings import get_settings
from .base_client import BaseHttpClient

logger = logging.getLogger(__name__)


class WeatherClient(BaseHttpClient):

    def __init__(self) -> None:
        super().__init__(base_url=OPENWEATHER_URL, timeout=15.0)

    def _api_key(self) -> str:
        return get_settings().openweather_api_key

    async def fetch_current(
        self,
        ciudad: str,
        departamento: Optional[str] = None,
    ) -> dict:
        api_key = self._api_key()
        if not api_key:
            return {
                "success": False,
                "message": "OPENWEATHER_API_KEY no configurada. Ver .env",
                "data": {},
            }

        params = {
            "q":     f"{ciudad},CO",
            "appid": api_key,
            "units": "metric",
            "lang":  "es",
        }

        raw = await self.get_safe("/weather", params=params, default=None)
        if not raw:
            return {"success": False, "message": "Sin respuesta de OpenWeather", "data": {}}

        return {
            "success":      True,
            "source":       "OpenWeather",
            "ciudad":       ciudad,
            "departamento": departamento,
            "condiciones": {
                "temperatura":       raw["main"]["temp"],
                "sensacion_termica": raw["main"]["feels_like"],
                "temperatura_max":   raw["main"]["temp_max"],
                "temperatura_min":   raw["main"]["temp_min"],
                "humedad":           raw["main"]["humidity"],
                "presion":           raw["main"]["pressure"],
                "descripcion":       raw["weather"][0]["description"],
                "nubosidad":         raw["clouds"]["all"],
                "viento_velocidad":  raw["wind"]["speed"],
                "visibilidad":       raw.get("visibility", 0),
            },
            "coordenadas":  {"lat": raw["coord"]["lat"], "lng": raw["coord"]["lon"]},
            "fetched_at":   datetime.utcnow().isoformat(),
        }
