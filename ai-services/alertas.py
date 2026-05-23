"""
AgroVision AI — Sistema de Alertas Inteligentes

Genera alertas automáticas combinando:
- Datos climáticos NASA POWER
- Predicciones del modelo ML
- Umbrales agronómicos por cultivo
"""

import httpx
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# ── Umbrales agronómicos por tipo de alerta ───────────────

UMBRALES = {
    "sequia": {
        "precipitacion_min": 5,      # mm/día promedio
        "humedad_min": 40,           # %
        "temperatura_max": 32,       # °C
        "dias_sin_lluvia": 7,        # días consecutivos
    },
    "inundacion": {
        "precipitacion_max": 60,     # mm/día promedio
        "humedad_max": 88,           # %
    },
    "helada": {
        "temperatura_min": 8,        # °C
    },
    "estres_termico": {
        "temperatura_max": 35,       # °C
        "humedad_min": 30,           # %
    },
}

CULTIVOS_VULNERABLES = {
    "sequia":         ["MAIZ", "FRIJOL", "ARROZ", "PAPA", "SORGO"],
    "inundacion":     ["ARROZ", "MAIZ", "PAPA", "CEBOLLA"],
    "helada":         ["PAPA", "FRIJOL", "ARVEJA", "TRIGO", "CEBADA"],
    "estres_termico": ["PAPA", "FRIJOL", "TOMATE", "ARVEJA"],
}

DEPARTAMENTOS_INFO = {
    "ANTIOQUIA":       {"lat": 6.2442,  "lng": -75.5812, "cultivos": ["CAFE", "MAIZ", "AGUACATE", "PAPA"]},
    "CUNDINAMARCA":    {"lat": 4.7110,  "lng": -74.0721, "cultivos": ["PAPA", "MAIZ", "FRIJOL", "ARROZ"]},
    "VALLE DEL CAUCA": {"lat": 3.4516,  "lng": -76.5320, "cultivos": ["CAÑA DE AZUCAR", "MAIZ", "SOYA"]},
    "TOLIMA":          {"lat": 4.4389,  "lng": -75.2322, "cultivos": ["ARROZ", "MAIZ", "SORGO", "CAFE"]},
    "META":            {"lat": 4.1420,  "lng": -73.6266, "cultivos": ["ARROZ", "MAIZ", "PALMA", "SOYA"]},
    "BOYACA":          {"lat": 5.5353,  "lng": -73.3678, "cultivos": ["PAPA", "MAIZ", "FRIJOL", "CEBOLLA"]},
    "CORDOBA":         {"lat": 8.7479,  "lng": -75.8814, "cultivos": ["MAIZ", "ARROZ", "ÑAME", "YUCA"]},
    "NARINO":          {"lat": 1.2136,  "lng": -77.2811, "cultivos": ["PAPA", "MAIZ", "CAFE", "FRIJOL"]},
    "SANTANDER":       {"lat": 7.1193,  "lng": -73.1227, "cultivos": ["CAFE", "MAIZ", "CACAO", "ARROZ"]},
    "HUILA":           {"lat": 2.9273,  "lng": -75.2819, "cultivos": ["CAFE", "ARROZ", "MAIZ", "SORGO"]},
}


# ── Fetch clima ───────────────────────────────────────────

async def fetch_clima_departamento(lat: float, lng: float, days: int = 14) -> dict:
    """Obtiene datos climáticos de NASA POWER."""
    from datetime import timedelta
    end = datetime.utcnow()
    start = end - timedelta(days=days)

    url = "https://power.larc.nasa.gov/api/temporal/daily/point"
    params = {
        "parameters": "T2M,PRECTOTCORR,RH2M",
        "community": "AG",
        "longitude": lng,
        "latitude": lat,
        "start": start.strftime("%Y%m%d"),
        "end": end.strftime("%Y%m%d"),
        "format": "JSON",
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.get(url, params=params)
            data = r.json()

        props = data.get("properties", {}).get("parameter", {})
        temp_vals = [v for v in props.get("T2M", {}).values() if v > -90]
        prec_vals = [v for v in props.get("PRECTOTCORR", {}).values() if v > -90]
        hum_vals  = [v for v in props.get("RH2M", {}).values() if v > -90]

        return {
            "temperatura_promedio": round(sum(temp_vals) / len(temp_vals), 2) if temp_vals else 0,
            "temperatura_max":      round(max(temp_vals), 2) if temp_vals else 0,
            "temperatura_min":      round(min(temp_vals), 2) if temp_vals else 0,
            "precipitacion_promedio": round(sum(prec_vals) / len(prec_vals), 2) if prec_vals else 0,
            "precipitacion_total":  round(sum(prec_vals), 2) if prec_vals else 0,
            "humedad_promedio":     round(sum(hum_vals) / len(hum_vals), 2) if hum_vals else 0,
            "dias_sin_lluvia":      sum(1 for v in prec_vals if v < 1),
        }
    except Exception as e:
        logger.error(f"Error NASA POWER: {e}")
        return {}


# ── Motor de alertas ──────────────────────────────────────

def evaluar_alertas(departamento: str, clima: dict, cultivos: list) -> list:
    """Evalúa condiciones climáticas y genera alertas."""
    alertas = []
    now = datetime.utcnow().isoformat()

    temp_prom = clima.get("temperatura_promedio", 0)
    temp_max  = clima.get("temperatura_max", 0)
    temp_min  = clima.get("temperatura_min", 0)
    prec_prom = clima.get("precipitacion_promedio", 0)
    humedad   = clima.get("humedad_promedio", 0)
    dias_seco = clima.get("dias_sin_lluvia", 0)

    # ── Alerta Sequía ──
    score_sequia = 0
    if prec_prom < UMBRALES["sequia"]["precipitacion_min"]:   score_sequia += 35
    if humedad   < UMBRALES["sequia"]["humedad_min"]:          score_sequia += 30
    if temp_prom > UMBRALES["sequia"]["temperatura_max"]:      score_sequia += 20
    if dias_seco >= UMBRALES["sequia"]["dias_sin_lluvia"]:     score_sequia += 15

    if score_sequia >= 30:
        severidad = "critica" if score_sequia >= 70 else "alta" if score_sequia >= 50 else "media"
        cultivos_afectados = [c for c in cultivos if c in CULTIVOS_VULNERABLES["sequia"]]
        alertas.append({
            "id": f"SEQ-{departamento[:3].upper()}-{datetime.utcnow().strftime('%Y%m%d')}",
            "tipo": "sequia",
            "severidad": severidad,
            "departamento": departamento,
            "titulo": f"Riesgo de Sequía en {departamento}",
            "mensaje": (
                f"Condiciones de sequía detectadas. Precipitación promedio: {prec_prom:.1f} mm/día, "
                f"Humedad: {humedad:.1f}%, Días sin lluvia: {dias_seco}. "
                f"Se recomienda activar sistemas de riego."
            ),
            "cultivos_afectados": cultivos_afectados,
            "variables": {"precipitacion": prec_prom, "humedad": humedad, "dias_secos": dias_seco},
            "recomendacion": "Activar riego suplementario. Monitorear reservas hídricas.",
            "score": score_sequia,
            "fecha": now,
            "activa": True,
        })

    # ── Alerta Inundación ──
    score_inund = 0
    if prec_prom > UMBRALES["inundacion"]["precipitacion_max"]: score_inund += 50
    if humedad   > UMBRALES["inundacion"]["humedad_max"]:        score_inund += 30
    if prec_prom > 40:                                           score_inund += 20

    if score_inund >= 30:
        severidad = "critica" if score_inund >= 70 else "alta" if score_inund >= 50 else "media"
        cultivos_afectados = [c for c in cultivos if c in CULTIVOS_VULNERABLES["inundacion"]]
        alertas.append({
            "id": f"INU-{departamento[:3].upper()}-{datetime.utcnow().strftime('%Y%m%d')}",
            "tipo": "inundacion",
            "severidad": severidad,
            "departamento": departamento,
            "titulo": f"Riesgo de Inundación en {departamento}",
            "mensaje": (
                f"Precipitación excesiva detectada. Promedio: {prec_prom:.1f} mm/día, "
                f"Humedad: {humedad:.1f}%. Se recomienda revisar drenajes."
            ),
            "cultivos_afectados": cultivos_afectados,
            "variables": {"precipitacion": prec_prom, "humedad": humedad},
            "recomendacion": "Verificar sistemas de drenaje. Cosechar cultivos maduros urgente.",
            "score": score_inund,
            "fecha": now,
            "activa": True,
        })

    # ── Alerta Helada ──
    if temp_min < UMBRALES["helada"]["temperatura_min"]:
        severidad = "critica" if temp_min < 2 else "alta" if temp_min < 5 else "media"
        cultivos_afectados = [c for c in cultivos if c in CULTIVOS_VULNERABLES["helada"]]
        alertas.append({
            "id": f"HEL-{departamento[:3].upper()}-{datetime.utcnow().strftime('%Y%m%d')}",
            "tipo": "helada",
            "severidad": severidad,
            "departamento": departamento,
            "titulo": f"Riesgo de Helada en {departamento}",
            "mensaje": (
                f"Temperatura mínima crítica: {temp_min:.1f}°C. "
                f"Riesgo de daño por helada en cultivos sensibles."
            ),
            "cultivos_afectados": cultivos_afectados,
            "variables": {"temperatura_min": temp_min, "temperatura_promedio": temp_prom},
            "recomendacion": "Aplicar coberturas protectoras. Riego nocturno preventivo.",
            "score": int((8 - temp_min) * 10),
            "fecha": now,
            "activa": True,
        })

    # ── Alerta Estrés Térmico ──
    if temp_max > UMBRALES["estres_termico"]["temperatura_max"] and humedad < UMBRALES["estres_termico"]["humedad_min"]:
        cultivos_afectados = [c for c in cultivos if c in CULTIVOS_VULNERABLES["estres_termico"]]
        alertas.append({
            "id": f"EST-{departamento[:3].upper()}-{datetime.utcnow().strftime('%Y%m%d')}",
            "tipo": "estres_termico",
            "severidad": "alta",
            "departamento": departamento,
            "titulo": f"Estrés Térmico en {departamento}",
            "mensaje": (
                f"Temperatura máxima: {temp_max:.1f}°C con humedad baja: {humedad:.1f}%. "
                f"Condiciones de estrés térmico para cultivos."
            ),
            "cultivos_afectados": cultivos_afectados,
            "variables": {"temperatura_max": temp_max, "humedad": humedad},
            "recomendacion": "Aumentar frecuencia de riego. Aplicar mulching para retener humedad.",
            "score": 60,
            "fecha": now,
            "activa": True,
        })

    return alertas


# ── Endpoint principal ────────────────────────────────────

async def generar_alertas_departamento(departamento: str) -> dict:
    """Genera alertas para un departamento específico."""
    info = DEPARTAMENTOS_INFO.get(departamento.upper())
    if not info:
        return {"success": False, "message": f"Departamento {departamento} no disponible"}

    clima = await fetch_clima_departamento(info["lat"], info["lng"])
    if not clima:
        return {"success": False, "message": "No se pudo obtener datos climáticos"}

    alertas = evaluar_alertas(departamento.upper(), clima, info["cultivos"])

    return {
        "success": True,
        "departamento": departamento.upper(),
        "clima_actual": clima,
        "total_alertas": len(alertas),
        "alertas": alertas,
        "fecha_generacion": datetime.utcnow().isoformat(),
    }


async def generar_alertas_nacional() -> dict:
    """Genera alertas para todos los departamentos."""
    import asyncio

    semaphore = asyncio.Semaphore(4)

    async def fetch_one(dept):
        async with semaphore:
            return await generar_alertas_departamento(dept)

    resultados = await asyncio.gather(
        *[fetch_one(d) for d in DEPARTAMENTOS_INFO.keys()],
        return_exceptions=True
    )

    todas_alertas = []
    for r in resultados:
        if isinstance(r, dict) and r.get("success"):
            todas_alertas.extend(r.get("alertas", []))

    # Ordenar por severidad
    orden = {"critica": 0, "alta": 1, "media": 2, "baja": 3}
    todas_alertas.sort(key=lambda x: orden.get(x.get("severidad", "baja"), 3))

    return {
        "success": True,
        "total_alertas": len(todas_alertas),
        "resumen": {
            "criticas": sum(1 for a in todas_alertas if a["severidad"] == "critica"),
            "altas":    sum(1 for a in todas_alertas if a["severidad"] == "alta"),
            "medias":   sum(1 for a in todas_alertas if a["severidad"] == "media"),
        },
        "alertas": todas_alertas,
        "fecha_generacion": datetime.utcnow().isoformat(),
    }
