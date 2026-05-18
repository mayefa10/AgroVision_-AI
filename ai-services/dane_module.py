"""
AgroVision AI — DANE / DIVIPOLA Module
Fuente 4: Georreferenciación oficial DANE

Datasets:
  - DIVIPOLA Municipios geolocalizados → vafm-j2df (con lat/lng)
  - DIVIPOLA Códigos municipios        → gdxc-w37w (códigos oficiales)
  - Departamentos + municipios         → xdk5-pm3f

100% datos abiertos — sin API key — Socrata API
"""
from typing import Optional
import httpx
import pandas as pd
from datetime import datetime
import logging

SOCRATA_BASE = "https://www.datos.gov.co/resource"
logger = logging.getLogger(__name__)

# ── DIVIPOLA endpoints ────────────────────────────────────

DIVIPOLA_GEO    = "vafm-j2df"   # Municipios con lat/lng
DIVIPOLA_CODIGOS = "gdxc-w37w"  # Códigos DANE oficiales
DANE_DEPTOS     = "xdk5-pm3f"   # Departamentos y municipios


async def fetch_divipola_geo(
    departamento: Optional[str] = None,
    limit: int = 1200
) -> dict:
    """
    DIVIPOLA con geolocalización — lat/lng por municipio.
    Fuente: DANE via datos.gov.co (vafm-j2df)
    
    Retorna código DANE, nombre municipio, departamento, lat, lng.
    Clave para hacer joins con EVA y pintar el mapa.
    """
    url = f"{SOCRATA_BASE}/{DIVIPOLA_GEO}.json"
    params = {"$limit": limit}
    
    if departamento:
        params["$where"] = f"upper(nom_dep)='{departamento.upper()}'"

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

        df = pd.DataFrame(data)
        if df.empty:
            return {"success": False, "message": "Sin datos", "data": []}

        # Estandarizar columnas — el dataset tiene variaciones de nombre
        col_map = {}
        for col in df.columns:
            low = col.lower()
            if "cod_mpio" in low or "codigo_municipio" in low or "cod_municipio" in low:
                col_map[col] = "codigo_municipio"
            elif "nom_mpio" in low or "nombre_municipio" in low or "municipio" in low:
                col_map[col] = "nombre_municipio"
            elif "nom_dep" in low or "nombre_departamento" in low or "departamento" in low:
                col_map[col] = "nombre_departamento"
            elif "cod_dep" in low or "codigo_departamento" in low:
                col_map[col] = "codigo_departamento"
            elif "latitud" in low or "lat" in low:
                col_map[col] = "latitud"
            elif "longitud" in low or "lng" in low or "lon" in low:
                col_map[col] = "longitud"
        
        df = df.rename(columns=col_map)

        # Extraer lat/lng de campo point si existen
        if "latitud" not in df.columns and "point" in df.columns:
            try:
                df["latitud"]  = df["point"].apply(lambda x: float(x.get("latitude", 0)) if isinstance(x, dict) else 0)
                df["longitud"] = df["point"].apply(lambda x: float(x.get("longitude", 0)) if isinstance(x, dict) else 0)
            except Exception:
                pass

        # Convertir numéricos
        for col in ["latitud", "longitud"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        return {
            "success": True,
            "source": "DANE — DIVIPOLA Geolocalizados (vafm-j2df)",
            "total_municipios": len(df),
            "departamento_filtro": departamento,
            "data": df.fillna("").to_dict(orient="records"),
            "fetched_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error DIVIPOLA geo: {e}")
        return {"success": False, "message": str(e), "data": []}


async def fetch_divipola_codigos(
    departamento: Optional[str] = None,
    codigo_municipio: Optional[str] = None,
    limit: int = 1200
) -> dict:
    """
    Códigos DANE oficiales (DIVIPOLA).
    Fuente: datos.gov.co (gdxc-w37w)
    
    Útil para:
    - Validar códigos antes de hacer joins con EVA
    - Lookup nombre → código y viceversa
    - Normalizar nombres de municipios
    """
    url = f"{SOCRATA_BASE}/{DIVIPOLA_CODIGOS}.json"
    params = {"$limit": limit}

    where = []
    if departamento:
        where.append(f"upper(nombre_departamento)='{departamento.upper()}'")
    if codigo_municipio:
        where.append(f"codigo_municipio='{codigo_municipio}'")
    if where:
        params["$where"] = " AND ".join(where)

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

        return {
            "success": True,
            "source": "DANE — DIVIPOLA Códigos (gdxc-w37w)",
            "total": len(data),
            "data": data,
            "fetched_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error DIVIPOLA codigos: {e}")
        return {"success": False, "message": str(e), "data": []}


async def fetch_dane_municipios_join(
    departamento: Optional[str] = None
) -> dict:
    """
    Pipeline de georreferenciación completo.
    Combina DIVIPOLA geo + códigos en un solo objeto limpio
    listo para hacer join con EVA.
    
    Output por municipio:
    {
        codigo_dane: "05001",
        nombre_municipio: "MEDELLÍN",
        nombre_departamento: "ANTIOQUIA",
        codigo_departamento: "05",
        lat: 6.2442,
        lng: -75.5812
    }
    """
    import asyncio

    geo_task    = fetch_divipola_geo(departamento=departamento)
    codigos_task = fetch_divipola_codigos(departamento=departamento)

    geo_result, codigos_result = await asyncio.gather(geo_task, codigos_task)

    # Usar geo como base si está disponible
    if geo_result.get("success") and geo_result.get("data"):
        df_geo = pd.DataFrame(geo_result["data"])

        # Asegurar campos mínimos
        required = ["codigo_municipio", "nombre_municipio", "nombre_departamento", "latitud", "longitud"]
        available = [c for c in required if c in df_geo.columns]

        result_data = df_geo[available].fillna("").to_dict(orient="records")
    elif codigos_result.get("success"):
        result_data = codigos_result["data"]
    else:
        result_data = []

    return {
        "success": True,
        "source": "DANE — DIVIPOLA (geo + códigos)",
        "total_municipios": len(result_data),
        "departamento": departamento,
        "data": result_data,
        "join_key": "codigo_municipio ↔ EVA.municipio (normalizar nombres)",
        "fetched_at": datetime.utcnow().isoformat()
    }


async def lookup_municipio(nombre: str) -> dict:
    """
    Busca un municipio por nombre y retorna su código DANE y coordenadas.
    Útil para el frontend: usuario escribe 'Medellín' y obtienes todo.
    """
    url = f"{SOCRATA_BASE}/{DIVIPOLA_CODIGOS}.json"
    params = {
        "$where": f"upper(nombre_municipio) like '%{nombre.upper()}%'",
        "$limit": 10
    }
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

        return {
            "success": True,
            "query": nombre,
            "resultados": len(data),
            "data": data
        }
    except Exception as e:
        return {"success": False, "message": str(e)}