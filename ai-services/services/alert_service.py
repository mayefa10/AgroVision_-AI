"""AgroVision AI — Servicio de alertas agroclimáticas."""
# Copyright (C) 2026 July Mayerly Quintero Farfán

from __future__ import annotations

import asyncio
import logging
from datetime import datetime

from app.config.constants import CULTIVOS_DEPTO, CULTIVOS_VULNERABLES, DEPARTAMENTOS, UMBRALES
from app.infrastructure.clients.nasa_client import NasaClient

logger = logging.getLogger(__name__)

_nasa = NasaClient()


# ── Helpers ───────────────────────────────────────────────

def _severidad(score: int) -> str:
    if score >= 70: return "critica"
    if score >= 50: return "alta"
    return "media"


def _build_alerta(
    *,
    tipo: str,
    prefijo: str,
    departamento: str,
    severidad: str,
    titulo: str,
    mensaje: str,
    cultivos_afectados: list[str],
    variables: dict,
    recomendacion: str,
    score: int,
    now: str,
) -> dict:
    fecha_key = datetime.utcnow().strftime("%Y%m%d")
    return {
        "id":                 f"{prefijo}-{departamento[:3].upper()}-{fecha_key}",
        "tipo":               tipo,
        "severidad":          severidad,
        "departamento":       departamento,
        "titulo":             titulo,
        "mensaje":            mensaje,
        "cultivos_afectados": cultivos_afectados,
        "variables":          variables,
        "recomendacion":      recomendacion,
        "score":              score,
        "fecha":              now,
        "activa":             True,
    }


# ── Motor de evaluación ───────────────────────────────────

def evaluar_alertas(departamento: str, clima: dict, cultivos: list[str]) -> list[dict]:
    alertas: list[dict] = []
    now = datetime.utcnow().isoformat()
    u   = UMBRALES

    temp_prom = clima.get("temperatura_promedio", 0)
    temp_max  = clima.get("temperatura_max", 0)
    temp_min  = clima.get("temperatura_min", 0)
    prec_prom = clima.get("precipitacion_promedio", 0)
    humedad   = clima.get("humedad_promedio", 0)
    dias_seco = clima.get("dias_sin_lluvia", 0)

    # Sequía
    sc = 0
    if prec_prom < u["sequia"]["precipitacion_min"]: sc += 35
    if humedad   < u["sequia"]["humedad_min"]:        sc += 30
    if temp_prom > u["sequia"]["temperatura_max"]:    sc += 20
    if dias_seco >= u["sequia"]["dias_sin_lluvia"]:   sc += 15
    if sc >= 30:
        alertas.append(_build_alerta(
            tipo="sequia", prefijo="SEQ", departamento=departamento,
            severidad=_severidad(sc),
            titulo=f"Riesgo de sequía en {departamento}",
            mensaje=(f"Precipitación: {prec_prom:.1f} mm/día, humedad: {humedad:.1f}%, "
                     f"días sin lluvia: {dias_seco}."),
            cultivos_afectados=[c for c in cultivos if c in CULTIVOS_VULNERABLES["sequia"]],
            variables={"precipitacion": prec_prom, "humedad": humedad, "dias_secos": dias_seco},
            recomendacion="Activar riego suplementario. Monitorear reservas hídricas.",
            score=sc, now=now,
        ))

    # Inundación
    sc = 0
    if prec_prom > u["inundacion"]["precipitacion_max"]:  sc += 50
    if humedad   > u["inundacion"]["humedad_max"]:         sc += 30
    if prec_prom > u["inundacion"]["precipitacion_alta"]:  sc += 20
    if sc >= 30:
        alertas.append(_build_alerta(
            tipo="inundacion", prefijo="INU", departamento=departamento,
            severidad=_severidad(sc),
            titulo=f"Riesgo de inundación en {departamento}",
            mensaje=f"Precipitación excesiva: {prec_prom:.1f} mm/día, humedad: {humedad:.1f}%.",
            cultivos_afectados=[c for c in cultivos if c in CULTIVOS_VULNERABLES["inundacion"]],
            variables={"precipitacion": prec_prom, "humedad": humedad},
            recomendacion="Verificar drenajes. Cosechar cultivos maduros urgente.",
            score=sc, now=now,
        ))

    # Helada
    if temp_min < u["helada"]["temperatura_min"]:
        if temp_min < u["helada"]["critica"]:  sev = "critica"
        elif temp_min < u["helada"]["alta"]:   sev = "alta"
        else:                                  sev = "media"
        sc_h = max(0, int((u["helada"]["temperatura_min"] - temp_min) * 10))
        alertas.append(_build_alerta(
            tipo="helada", prefijo="HEL", departamento=departamento,
            severidad=sev,
            titulo=f"Riesgo de helada en {departamento}",
            mensaje=f"Temperatura mínima crítica: {temp_min:.1f}°C.",
            cultivos_afectados=[c for c in cultivos if c in CULTIVOS_VULNERABLES["helada"]],
            variables={"temperatura_min": temp_min, "temperatura_promedio": temp_prom},
            recomendacion="Aplicar coberturas protectoras. Riego nocturno preventivo.",
            score=sc_h, now=now,
        ))

    # Estrés térmico
    if temp_max > u["estres_termico"]["temperatura_max"] and humedad < u["estres_termico"]["humedad_min"]:
        alertas.append(_build_alerta(
            tipo="estres_termico", prefijo="EST", departamento=departamento,
            severidad="alta",
            titulo=f"Estrés térmico en {departamento}",
            mensaje=f"Temperatura máxima: {temp_max:.1f}°C con humedad baja: {humedad:.1f}%.",
            cultivos_afectados=[c for c in cultivos if c in CULTIVOS_VULNERABLES["estres_termico"]],
            variables={"temperatura_max": temp_max, "humedad": humedad},
            recomendacion="Aumentar frecuencia de riego. Aplicar mulching.",
            score=60, now=now,
        ))

    return alertas


# ── API pública ───────────────────────────────────────────

async def get_alertas_departamento(departamento: str) -> dict:
    info = DEPARTAMENTOS.get(departamento.upper())
    if not info:
        return {"success": False, "message": f"Departamento '{departamento}' no disponible"}

    nasa = await _nasa.fetch_daily(info["lat"], info["lng"], days=14, departamento=departamento)
    if not nasa.get("success"):
        return {"success": False, "message": "No se pudo obtener datos climáticos"}

    cultivos = CULTIVOS_DEPTO.get(departamento.upper(), [])
    alertas  = evaluar_alertas(departamento.upper(), nasa["estadisticas"], cultivos)

    return {
        "success":          True,
        "departamento":     departamento.upper(),
        "clima_actual":     nasa["estadisticas"],
        "total_alertas":    len(alertas),
        "alertas":          alertas,
        "fecha_generacion": datetime.utcnow().isoformat(),
    }


async def get_alertas_nacional() -> dict:
    semaphore = asyncio.Semaphore(4)

    async def one(dept: str) -> dict:
        async with semaphore:
            return await get_alertas_departamento(dept)

    results = await asyncio.gather(
        *[one(d) for d in CULTIVOS_DEPTO],
        return_exceptions=True,
    )

    todas: list[dict] = []
    for r in results:
        if isinstance(r, dict) and r.get("success"):
            todas.extend(r.get("alertas", []))

    orden = {"critica": 0, "alta": 1, "media": 2, "baja": 3}
    todas.sort(key=lambda a: orden.get(a.get("severidad", "baja"), 3))

    return {
        "success":       True,
        "total_alertas": len(todas),
        "resumen": {
            "criticas": sum(1 for a in todas if a["severidad"] == "critica"),
            "altas":    sum(1 for a in todas if a["severidad"] == "alta"),
            "medias":   sum(1 for a in todas if a["severidad"] == "media"),
        },
        "alertas":           todas,
        "fecha_generacion":  datetime.utcnow().isoformat(),
    }
