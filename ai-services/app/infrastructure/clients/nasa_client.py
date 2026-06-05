"""AgroVision AI — Cliente NASA POWER."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from app.config.constants import NASA_ANNUAL_URL, NASA_DAILY_URL
from .base_client import BaseHttpClient

logger = logging.getLogger(__name__)

NASA_PARAMS_DAILY  = "T2M,PRECTOTCORR,RH2M,ALLSKY_SFC_SW_DWN,WS2M"
NASA_PARAMS_ANNUAL = "T2M,PRECTOTCORR,RH2M,ALLSKY_SFC_SW_DWN"


def _clean_vals(raw: dict, key: str) -> list[float]:
    """Filtra valores inválidos NASA (< -90 = sin dato)."""
    return [v for v in raw.get(key, {}).values() if v > -90]


class NasaClient(BaseHttpClient):

    def __init__(self) -> None:
        super().__init__(timeout=60.0)

    async def fetch_daily(
        self,
        lat: float,
        lng: float,
        days: int = 30,
        departamento: Optional[str] = None,
    ) -> dict:
        """Datos diarios de los últimos `days` días."""
        end = datetime.now(timezone.utc)
        start = end - timedelta(days=days)

        params = {
            "parameters": NASA_PARAMS_DAILY,
            "community":  "AG",
            "longitude":  lng,
            "latitude":   lat,
            "start":      start.strftime("%Y%m%d"),
            "end":        end.strftime("%Y%m%d"),
            "format":     "JSON",
        }

        raw = await self.get_safe(NASA_DAILY_URL, params=params, default={})
        if not raw:
            return {"success": False, "message": "Sin respuesta de NASA POWER", "data": []}

        props = raw.get("properties", {}).get("parameter", {})
        temp  = _clean_vals(props, "T2M")
        prec  = _clean_vals(props, "PRECTOTCORR")
        hum   = _clean_vals(props, "RH2M")

        dates   = list(props.get("T2M", {}).keys())
        records = [
            {
                "fecha":          d,
                "temperatura":    round(props["T2M"].get(d, 0), 2),
                "precipitacion":  round(props.get("PRECTOTCORR", {}).get(d, 0), 2),
                "humedad":        round(props.get("RH2M", {}).get(d, 0), 2),
                "radiacion_solar":round(props.get("ALLSKY_SFC_SW_DWN", {}).get(d, 0), 2),
                "viento":         round(props.get("WS2M", {}).get(d, 0), 2),
            }
            for d in dates
        ]

        estadisticas = {
            "temperatura_promedio":   round(sum(temp) / len(temp), 2) if temp else 0,
            "temperatura_max":        round(max(temp), 2) if temp else 0,
            "temperatura_min":        round(min(temp), 2) if temp else 0,
            "precipitacion_promedio": round(sum(prec) / len(prec), 2) if prec else 0,
            "precipitacion_total":    round(sum(prec), 2) if prec else 0,
            "humedad_promedio":       round(sum(hum) / len(hum), 2) if hum else 0,
            "dias_sin_lluvia":        sum(1 for v in prec if v < 1),
            "dias_con_lluvia":        sum(1 for v in prec if v >= 1),
        }

        return {
            "success":      True,
            "source":       "NASA POWER",
            "departamento": departamento,
            "coordenadas":  {"lat": lat, "lng": lng},
            "periodo": {
                "inicio": start.strftime("%Y-%m-%d"),
                "fin":    end.strftime("%Y-%m-%d"),
                "dias":   days,
            },
            "estadisticas": estadisticas,
            "data":         records,
            "fetched_at":   datetime.utcnow().isoformat(),
        }

    async def fetch_annual(
        self,
        lat: float,
        lng: float,
        anio: int,
        departamento: Optional[str] = None,
    ) -> dict:
        """Promedio anual para un año específico."""
        params = {
            "parameters": NASA_PARAMS_ANNUAL,
            "community":  "AG",
            "longitude":  lng,
            "latitude":   lat,
            "start":      anio,
            "end":        anio,
            "format":     "JSON",
        }
        raw = await self.get_safe(NASA_ANNUAL_URL, params=params, default={})
        if not raw:
            return {"departamento": departamento, "anio": anio}

        props = raw.get("properties", {}).get("parameter", {})

        def first_val(key: str) -> Optional[float]:
            vals = list(props.get(key, {}).values())
            return vals[0] if vals else None

        return {
            "departamento":  departamento,
            "anio":          anio,
            "temp_promedio": first_val("T2M"),
            "precipitacion": first_val("PRECTOTCORR"),
            "humedad":       first_val("RH2M"),
            "radiacion_solar": first_val("ALLSKY_SFC_SW_DWN"),
        }
