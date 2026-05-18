"""
AgroVision AI — Data Pipeline
Ingesta de datos desde:
  1. EVA (datos.gov.co) — Evaluaciones Agropecuarias Municipales
  2. NASA POWER         — Datos agroclimáticos históricos
  3. OpenWeather        — Clima en tiempo real
"""

import httpx
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional
import os
import logging

logger = logging.getLogger(__name__)

# ── Configuración ─────────────────────────────────────────

SOCRATA_BASE   = "https://www.datos.gov.co/resource"
EVA_2019_2024  = "uejq-wxrr"   # EVA Base Agrícola 2019-2024
EVA_HISTORICO  = "2pnw-mmge"   # EVA histórico completo
NASA_POWER_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5"
OW_API_KEY     = os.getenv("OPENWEATHER_API_KEY", "")

# Coordenadas de capitales departamentales de Colombia
DEPARTAMENTOS = {
    "ANTIOQUIA":       {"lat": 6.2442,  "lng": -75.5812, "capital": "Medellin"},
    "ATLANTICO":       {"lat": 10.9639, "lng": -74.7964, "capital": "Barranquilla"},
    "BOLIVAR":         {"lat": 10.3910, "lng": -75.4794, "capital": "Cartagena"},
    "BOYACA":          {"lat": 5.5353,  "lng": -73.3678, "capital": "Tunja"},
    "CALDAS":          {"lat": 5.0689,  "lng": -75.5174, "capital": "Manizales"},
    "CAQUETA":         {"lat": 1.6144,  "lng": -75.6062, "capital": "Florencia"},
    "CAUCA":           {"lat": 2.4448,  "lng": -76.6147, "capital": "Popayan"},
    "CESAR":           {"lat": 10.4631, "lng": -73.2532, "capital": "Valledupar"},
    "CHOCO":           {"lat": 5.6920,  "lng": -76.6583, "capital": "Quibdo"},
    "CORDOBA":         {"lat": 8.7479,  "lng": -75.8814, "capital": "Monteria"},
    "CUNDINAMARCA":    {"lat": 4.7110,  "lng": -74.0721, "capital": "Bogota"},
    "GUAJIRA":         {"lat": 11.5444, "lng": -72.9072, "capital": "Riohacha"},
    "HUILA":           {"lat": 2.9273,  "lng": -75.2819, "capital": "Neiva"},
    "MAGDALENA":       {"lat": 11.2408, "lng": -74.1990, "capital": "Santa Marta"},
    "META":            {"lat": 4.1420,  "lng": -73.6266, "capital": "Villavicencio"},
    "NARINO":          {"lat": 1.2136,  "lng": -77.2811, "capital": "Pasto"},
    "NORTE DE SANTANDER": {"lat": 7.8939, "lng": -72.5078, "capital": "Cucuta"},
    "SANTANDER":       {"lat": 7.1193,  "lng": -73.1227, "capital": "Bucaramanga"},
    "SUCRE":           {"lat": 9.3047,  "lng": -75.3978, "capital": "Sincelejo"},
    "TOLIMA":          {"lat": 4.4389,  "lng": -75.2322, "capital": "Ibague"},
    "VALLE DEL CAUCA": {"lat": 3.4516,  "lng": -76.5320, "capital": "Cali"},
}

# ── 1. EVA — Evaluaciones Agropecuarias ───────────────────

async def fetch_eva_data(
    departamento: Optional[str] = None,
    cultivo: Optional[str] = None,
    anio: Optional[int] = None,
    limit: int = 1000,
    dataset: str = EVA_2019_2024
) -> dict:
    """
    Consulta el dataset EVA desde datos.gov.co via Socrata API.
    
    Parámetros:
        departamento: Nombre del departamento (ej: 'ANTIOQUIA')
        cultivo: Nombre del cultivo (ej: 'MAIZ')
        anio: Año de consulta (ej: 2023)
        limit: Número máximo de registros
        dataset: ID del dataset Socrata
    
    Retorna dict con data y metadata
    """
    url = f"{SOCRATA_BASE}/{dataset}.json"
    
    # Construir query SoQL
    where_clauses = []
    if departamento:
        where_clauses.append(f"upper(departamento)='{departamento.upper()}'")
    if cultivo:
        where_clauses.append(f"upper(cultivo)='{cultivo.upper()}'")
    if anio:
        where_clauses.append(f"a_o={anio}")
    
    params = {
        "$limit": limit,
        "$order": "a_o DESC",
    }
    if where_clauses:
        params["$where"] = " AND ".join(where_clauses)

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            
            # Procesar con pandas
            df = pd.DataFrame(data)
            
            if df.empty:
                return {"success": False, "message": "No se encontraron datos", "data": []}
            
            # Limpiar y tipar columnas numéricas
            numeric_cols = ["area_sembrada", "area_cosechada", "produccion", "rendimiento"]
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")
            
            # Estadísticas básicas
            stats = {}
            if "rendimiento" in df.columns:
                stats["rendimiento_promedio"] = round(df["rendimiento"].mean(), 2)
                stats["rendimiento_max"]       = round(df["rendimiento"].max(), 2)
                stats["rendimiento_min"]       = round(df["rendimiento"].min(), 2)
            if "produccion" in df.columns:
                stats["produccion_total"] = round(df["produccion"].sum(), 2)
            if "area_sembrada" in df.columns:
                stats["area_sembrada_total"] = round(df["area_sembrada"].sum(), 2)

            return {
                "success": True,
                "source": "EVA — datos.gov.co",
                "dataset_id": dataset,
                "total_registros": len(df),
                "filtros": {
                    "departamento": departamento,
                    "cultivo": cultivo,
                    "anio": anio
                },
                "estadisticas": stats,
                "data": df.fillna(0).to_dict(orient="records"),
                "fetched_at": datetime.utcnow().isoformat()
            }
            
    except httpx.HTTPError as e:
        logger.error(f"Error fetching EVA data: {e}")
        return {"success": False, "message": str(e), "data": []}


async def fetch_eva_summary() -> dict:
    """Resumen nacional de EVA — top cultivos y departamentos."""
    url = f"{SOCRATA_BASE}/{EVA_2019_2024}.json"
    params = {
        "$select": "departamento, cultivo, sum(produccion) as produccion_total, sum(area_sembrada) as area_total, avg(rendimiento) as rendimiento_promedio, max(a_o) as ultimo_anio",
        "$group": "departamento, cultivo",
        "$order": "produccion_total DESC",
        "$limit": 50,
    }
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            df = pd.DataFrame(data)
            for col in ["produccion_total", "area_total", "rendimiento_promedio"]:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce").round(2)
            return {
                "success": True,
                "source": "EVA — datos.gov.co",
                "data": df.fillna(0).to_dict(orient="records"),
                "fetched_at": datetime.utcnow().isoformat()
            }
    except Exception as e:
        return {"success": False, "message": str(e), "data": []}


# ── 2. NASA POWER — Datos Agroclimáticos ─────────────────

async def fetch_nasa_power(
    lat: float,
    lng: float,
    days: int = 30,
    departamento: Optional[str] = None
) -> dict:
    """
    Consulta NASA POWER API para datos agroclimáticos.
    Sin API key — completamente abierta.
    
    Parámetros:
        lat, lng: Coordenadas
        days: Días hacia atrás desde hoy
        departamento: Nombre descriptivo
    
    Variables:
        T2M         — Temperatura a 2m (°C)
        PRECTOTCORR — Precipitación corregida (mm/día)
        RH2M        — Humedad relativa a 2m (%)
        ALLSKY_SFC_SW_DWN — Radiación solar (MJ/m²/día)
        WS2M        — Velocidad del viento a 2m (m/s)
    """
    end_date   = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    params = {
        "parameters": "T2M,PRECTOTCORR,RH2M,ALLSKY_SFC_SW_DWN,WS2M",
        "community": "AG",
        "longitude": lng,
        "latitude": lat,
        "start": start_date.strftime("%Y%m%d"),
        "end": end_date.strftime("%Y%m%d"),
        "format": "JSON",
    }
    
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.get(NASA_POWER_URL, params=params)
            resp.raise_for_status()
            raw = resp.json()
        
        props = raw.get("properties", {}).get("parameter", {})
        
        # Construir DataFrame
        dates = list(props.get("T2M", {}).keys())
        records = []
        for d in dates:
            records.append({
                "fecha": d,
                "temperatura": round(props.get("T2M", {}).get(d, 0), 2),
                "precipitacion": round(props.get("PRECTOTCORR", {}).get(d, 0), 2),
                "humedad": round(props.get("RH2M", {}).get(d, 0), 2),
                "radiacion_solar": round(props.get("ALLSKY_SFC_SW_DWN", {}).get(d, 0), 2),
                "viento": round(props.get("WS2M", {}).get(d, 0), 2),
            })
        
        df = pd.DataFrame(records)
        
        # Estadísticas del período
        stats = {
            "temperatura_promedio": round(df["temperatura"].mean(), 2),
            "temperatura_max":      round(df["temperatura"].max(), 2),
            "temperatura_min":      round(df["temperatura"].min(), 2),
            "precipitacion_total":  round(df["precipitacion"].sum(), 2),
            "humedad_promedio":     round(df["humedad"].mean(), 2),
            "dias_sin_lluvia":      int((df["precipitacion"] < 1).sum()),
            "dias_con_lluvia":      int((df["precipitacion"] >= 1).sum()),
        }
        
        return {
            "success": True,
            "source": "NASA POWER",
            "departamento": departamento,
            "coordenadas": {"lat": lat, "lng": lng},
            "periodo": {
                "inicio": start_date.strftime("%Y-%m-%d"),
                "fin": end_date.strftime("%Y-%m-%d"),
                "dias": days
            },
            "estadisticas": stats,
            "data": records,
            "fetched_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching NASA POWER: {e}")
        return {"success": False, "message": str(e), "data": []}


async def fetch_nasa_all_departments(days: int = 30) -> dict:
    """Fetch clima para todos los departamentos en paralelo."""
    import asyncio
    
    tasks = []
    dept_list = list(DEPARTAMENTOS.items())
    
    # Limitar a 10 concurrentes para no sobrecargar NASA
    semaphore = asyncio.Semaphore(5)
    
    async def fetch_one(name, info):
        async with semaphore:
            result = await fetch_nasa_power(
                lat=info["lat"],
                lng=info["lng"],
                days=days,
                departamento=name
            )
            return {"departamento": name, **result}
    
    results = await asyncio.gather(
        *[fetch_one(name, info) for name, info in dept_list],
        return_exceptions=True
    )
    
    successful = [r for r in results if isinstance(r, dict) and r.get("success")]
    
    return {
        "success": True,
        "total_departamentos": len(successful),
        "data": successful,
        "fetched_at": datetime.utcnow().isoformat()
    }


# ── 3. OpenWeather — Tiempo Real ──────────────────────────

async def fetch_openweather(ciudad: str, departamento: Optional[str] = None) -> dict:
    """
    Consulta OpenWeather para condiciones actuales.
    Requiere OPENWEATHER_API_KEY en variables de entorno.
    """
    if not OW_API_KEY:
        return {
            "success": False,
            "message": "OPENWEATHER_API_KEY no configurada. Ver .env",
            "data": {}
        }
    
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                f"{OPENWEATHER_URL}/weather",
                params={
                    "q": f"{ciudad},CO",
                    "appid": OW_API_KEY,
                    "units": "metric",
                    "lang": "es"
                }
            )
            resp.raise_for_status()
            raw = resp.json()
        
        return {
            "success": True,
            "source": "OpenWeather",
            "ciudad": ciudad,
            "departamento": departamento,
            "condiciones": {
                "temperatura": raw["main"]["temp"],
                "sensacion_termica": raw["main"]["feels_like"],
                "temperatura_max": raw["main"]["temp_max"],
                "temperatura_min": raw["main"]["temp_min"],
                "humedad": raw["main"]["humidity"],
                "presion": raw["main"]["pressure"],
                "descripcion": raw["weather"][0]["description"],
                "nubosidad": raw["clouds"]["all"],
                "viento_velocidad": raw["wind"]["speed"],
                "visibilidad": raw.get("visibility", 0),
            },
            "coordenadas": {
                "lat": raw["coord"]["lat"],
                "lng": raw["coord"]["lon"]
            },
            "fetched_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {"success": False, "message": str(e), "data": {}}


async def fetch_openweather_all() -> dict:
    """Fetch clima actual para todas las capitales."""
    import asyncio
    
    tasks = [
        fetch_openweather(info["capital"], name)
        for name, info in DEPARTAMENTOS.items()
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    successful = [r for r in results if isinstance(r, dict) and r.get("success")]
    
    return {
        "success": True,
        "total": len(successful),
        "data": successful,
        "fetched_at": datetime.utcnow().isoformat()
    }


# ── 4. Pipeline combinado ─────────────────────────────────

async def fetch_full_pipeline(departamento: str, cultivo: str = "MAIZ") -> dict:
    """
    Pipeline completo para un departamento:
    EVA + NASA POWER + OpenWeather → datos listos para ML
    """
    import asyncio
    
    info = DEPARTAMENTOS.get(departamento.upper(), {
        "lat": 4.7110, "lng": -74.0721, "capital": "Bogota"
    })
    
    eva_task      = fetch_eva_data(departamento=departamento, cultivo=cultivo)
    nasa_task     = fetch_nasa_power(lat=info["lat"], lng=info["lng"], departamento=departamento)
    weather_task  = fetch_openweather(info["capital"], departamento)
    
    eva_data, nasa_data, weather_data = await asyncio.gather(
        eva_task, nasa_task, weather_task
    )
    
    return {
        "departamento": departamento,
        "cultivo": cultivo,
        "eva": eva_data,
        "clima_historico": nasa_data,
        "clima_actual": weather_data,
        "pipeline_at": datetime.utcnow().isoformat()
    }
