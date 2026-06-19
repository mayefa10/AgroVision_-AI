"""
AgroVision AI — Cliente NOAA.
Obtiene el Oceanic Niño Index (ONI) desde NOAA/CPC.
URL: https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt
Formato: texto plano — NO JSON.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

NOAA_ONI_URL = "https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt"

_SEASON_MONTHS = {
    "DJF": 1, "JFM": 2, "FMA": 3, "MAM": 4, "AMJ": 5, "MJJ": 6,
    "JJA": 7, "JAS": 8, "ASO": 9, "SON": 10, "OND": 11, "NDJ": 12,
}


def _clasificar_oni(oni: float) -> dict:
    if oni >= 2.0:
        return {"fase": "El Nino", "intensidad": "muy_fuerte", "color": "#dc2626"}
    if oni >= 1.5:
        return {"fase": "El Nino", "intensidad": "fuerte",     "color": "#ef4444"}
    if oni >= 1.0:
        return {"fase": "El Nino", "intensidad": "moderado",   "color": "#f97316"}
    if oni >= 0.5:
        return {"fase": "El Nino", "intensidad": "debil",      "color": "#f59e0b"}
    if oni <= -2.0:
        return {"fase": "La Nina", "intensidad": "muy_fuerte", "color": "#1d4ed8"}
    if oni <= -1.5:
        return {"fase": "La Nina", "intensidad": "fuerte",     "color": "#2563eb"}
    if oni <= -1.0:
        return {"fase": "La Nina", "intensidad": "moderado",   "color": "#3b82f6"}
    if oni <= -0.5:
        return {"fase": "La Nina", "intensidad": "debil",      "color": "#60a5fa"}
    return {"fase": "Neutro", "intensidad": "neutro", "color": "#16a34a"}


def _impacto_colombia(fase: str) -> dict:
    if fase == "El Nino":
        return {
            "precipitacion":     "↓ Déficit hídrico — lluvias por debajo del promedio",
            "temperatura":       "↑ Temperaturas más altas de lo normal",
            "riesgo_sequia":     "Alto",
            "riesgo_inundacion": "Bajo",
            "cultivos_riesgo":   ["MAIZ", "FRIJOL", "ARROZ", "PAPA"],
            "recomendacion":     "Activar sistemas de riego. Reservar agua en épocas de lluvia.",
            "alerta":            "⚠️ Temporada seca más intensa de lo normal",
        }
    if fase == "La Nina":
        return {
            "precipitacion":     "↑ Exceso hídrico — lluvias por encima del promedio",
            "temperatura":       "↓ Temperaturas más bajas de lo normal",
            "riesgo_sequia":     "Bajo",
            "riesgo_inundacion": "Alto",
            "cultivos_riesgo":   ["PAPA", "CAFE", "MAIZ", "CEBOLLA"],
            "recomendacion":     "Mejorar sistemas de drenaje. Vigilar enfermedades fungosas.",
            "alerta":            "🌊 Riesgo de exceso hídrico e inundaciones",
        }
    return {
        "precipitacion":     "→ Lluvias dentro del rango histórico normal",
        "temperatura":       "→ Temperaturas dentro del rango histórico normal",
        "riesgo_sequia":     "Normal",
        "riesgo_inundacion": "Normal",
        "cultivos_riesgo":   [],
        "recomendacion":     "Condiciones normales. Seguir calendario agrícola estándar.",
        "alerta":            "✅ Condiciones climáticas dentro de los parámetros normales",
    }


async def _fetch_oni_texto(anios: int = 5) -> list[dict]:
    """Descarga el ONI como texto plano y parsea los registros."""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.get(NOAA_ONI_URL)
            r.raise_for_status()
            texto = r.text
    except Exception as e:
        logger.error("Error descargando ONI NOAA: %s", e)
        return []

    anio_corte = datetime.now(timezone.utc).year - anios
    registros  = []

    for linea in texto.strip().split("\n"):
        partes = linea.split()
        if len(partes) < 3:
            continue
        try:
            season = partes[0]
            anio   = int(partes[1])
            oni    = float(partes[2])
        except (ValueError, IndexError):
            continue

        if anio < anio_corte:
            continue

        clas = _clasificar_oni(oni)
        registros.append({
            "season":     season,
            "anio":       anio,
            "oni_index":  oni,
            "fase":       clas["fase"],
            "intensidad": clas["intensidad"],
            "color":      clas["color"],
            "mes_ref":    _SEASON_MONTHS.get(season, 0),
        })

    return registros


class NoaaClient:

    async def fetch_oni_historico(self, anios: int = 5) -> dict:
        registros = await _fetch_oni_texto(anios)
        if not registros:
            return {"success": False, "message": "No se pudo conectar con NOAA/CPC", "data": []}

        actual  = registros[-1]
        impacto = _impacto_colombia(actual["fase"])

        return {
            "success":         True,
            "source":          "NOAA/CPC — Oceanic Niño Index",
            "actual":          {**actual, "impacto_colombia": impacto},
            "historico":       registros,
            "total_registros": len(registros),
            "fetched_at":      datetime.now(timezone.utc).isoformat(),
        }

    async def fetch_enso_actual(self) -> dict:
        oni_data = await self.fetch_oni_historico(anios=3)
        if not oni_data.get("success"):
            return oni_data

        actual    = oni_data["actual"]
        historico = oni_data["historico"]

        # Tendencia: comparar últimos 3 registros
        ultimos   = historico[-3:] if len(historico) >= 3 else historico
        tendencia = "estable"
        if len(ultimos) >= 2:
            delta = ultimos[-1]["oni_index"] - ultimos[0]["oni_index"]
            if delta > 0.3:
                tendencia = "intensificando"
            elif delta < -0.3:
                tendencia = "debilitando"

        # Probabilidades estimadas desde ONI actual
        oni_val      = actual["oni_index"]
        prob_el_nino = max(0, min(100, int(50 + oni_val * 25)))
        prob_la_nina = max(0, min(100, int(50 - oni_val * 25)))
        prob_neutro  = max(0, 100 - prob_el_nino - prob_la_nina)

        return {
            "success": True,
            "source":  "NOAA/CPC — Oceanic Niño Index (ONI)",
            "estado_actual": {
                "fase":       actual["fase"],
                "intensidad": actual["intensidad"],
                "oni_index":  actual["oni_index"],
                "season":     actual["season"],
                "anio":       actual["anio"],
                "color":      actual["color"],
                "tendencia":  tendencia,
            },
            "probabilidades": {
                "el_nino": prob_el_nino,
                "la_nina": prob_la_nina,
                "neutro":  prob_neutro,
            },
            "impacto_colombia": actual["impacto_colombia"],
            "historico_oni":    historico[-12:],
            "fetched_at":       datetime.now(timezone.utc).isoformat(),
        }

    async def fetch_escenarios(
        self,
        departamento: str = "ANTIOQUIA",
        cultivo: str = "MAIZ",
    ) -> dict:
        enso = await self.fetch_enso_actual()
        if not enso.get("success"):
            return enso

        oni_actual = enso["estado_actual"]["oni_index"]

        escenario_el_nino = {
            "nombre":      "El Niño",
            "descripcion": "Si precipitaciones ↓35% y temperatura ↑1.5°C",
            "icono":       "☀️",
            "color":       "#ef4444",
            "condiciones": {"precipitacion_cambio": -35, "temperatura_cambio": +1.5},
            "impactos": {
                "produccion_estimada": -18,
                "riesgo_agricola":     "Alto",
                "riesgo_sequia":       "Muy Alto",
                "riesgo_incendios":    "Alto",
            },
            "cultivos_criticos": ["MAIZ", "FRIJOL", "ARROZ", "PAPA"],
            "recomendaciones": [
                "Activar sistemas de riego suplementario",
                "Reservar agua en épocas de lluvia",
                "Diversificar hacia cultivos resistentes a sequía",
                "Contratar seguro agrícola antes de la temporada",
            ],
        }

        escenario_la_nina = {
            "nombre":      "La Niña",
            "descripcion": "Si precipitaciones ↑40% y temperatura ↓0.8°C",
            "icono":       "🌊",
            "color":       "#3b82f6",
            "condiciones": {"precipitacion_cambio": +40, "temperatura_cambio": -0.8},
            "impactos": {
                "produccion_estimada": -8,
                "riesgo_agricola":     "Medio-Alto",
                "riesgo_fitosanitario":"Alto",
                "riesgo_inundacion":   "Muy Alto",
            },
            "cultivos_criticos": ["PAPA", "CAFE", "CEBOLLA", "FRIJOL"],
            "recomendaciones": [
                "Mejorar sistemas de drenaje",
                "Aplicar fungicidas preventivos",
                "Adelantar cosechas de cultivos maduros",
                "Monitorear deslizamientos en zonas de ladera",
            ],
        }

        escenario_activo = None
        if oni_actual >= 0.5:
            escenario_activo = "El Nino"
        elif oni_actual <= -0.5:
            escenario_activo = "La Nina"

        return {
            "success":          True,
            "departamento":     departamento,
            "cultivo":          cultivo,
            "oni_actual":       oni_actual,
            "escenario_activo": escenario_activo,
            "escenarios": {
                "el_nino": escenario_el_nino,
                "la_nina": escenario_la_nina,
            },
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }


# Singleton
noaa_client = NoaaClient()