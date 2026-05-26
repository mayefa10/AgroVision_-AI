"""
AgroVision AI — ETL Pipeline
Construye el dataset maestro combinando:
  1. EVA (datos.gov.co) — producción agrícola 2007-2024
  2. NASA POWER — clima histórico por departamento
  3. ENSO index — fases El Niño / La Niña

Unidad de análisis: departamento + cultivo + año + semestre
Target: rendimiento (t/ha)
"""

import httpx
import pandas as pd
import numpy as np
from datetime import datetime
import asyncio
import logging
import os

logger = logging.getLogger(__name__)

# ── Configuración ─────────────────────────────────────────

DATASETS_PATH = "/app/datasets"
RAW_PATH      = f"{DATASETS_PATH}/raw"
PROCESSED_PATH = f"{DATASETS_PATH}/processed"
FEATURES_PATH  = f"{DATASETS_PATH}/features"

for path in [RAW_PATH, PROCESSED_PATH, FEATURES_PATH]:
    os.makedirs(path, exist_ok=True)

# Departamentos con coordenadas
DEPARTAMENTOS_GEO = {
    "ANTIOQUIA":       {"lat": 6.2442,  "lng": -75.5812, "codigo": "05"},
    "ATLANTICO":       {"lat": 10.9639, "lng": -74.7964, "codigo": "08"},
    "BOLIVAR":         {"lat": 8.6706,  "lng": -74.0328, "codigo": "13"},
    "BOYACA":          {"lat": 5.5353,  "lng": -73.3678, "codigo": "15"},
    "CALDAS":          {"lat": 5.0689,  "lng": -75.5174, "codigo": "17"},
    "CAUCA":           {"lat": 2.4448,  "lng": -76.6147, "codigo": "19"},
    "CESAR":           {"lat": 10.4631, "lng": -73.2532, "codigo": "20"},
    "CORDOBA":         {"lat": 8.7479,  "lng": -75.8814, "codigo": "23"},
    "CUNDINAMARCA":    {"lat": 4.7110,  "lng": -74.0721, "codigo": "25"},
    "HUILA":           {"lat": 2.9273,  "lng": -75.2819, "codigo": "41"},
    "MAGDALENA":       {"lat": 10.4195, "lng": -74.4061, "codigo": "47"},
    "META":            {"lat": 4.1420,  "lng": -73.6266, "codigo": "50"},
    "NARINO":          {"lat": 1.2136,  "lng": -77.2811, "codigo": "52"},
    "NORTE DE SANTANDER": {"lat": 7.8939, "lng": -72.5078, "codigo": "54"},
    "SANTANDER":       {"lat": 7.1193,  "lng": -73.1227, "codigo": "68"},
    "TOLIMA":          {"lat": 4.4389,  "lng": -75.2322, "codigo": "73"},
    "VALLE DEL CAUCA": {"lat": 3.4516,  "lng": -76.5320, "codigo": "76"},
}

# ── ENSO histórico (ONI index simplificado) ───────────────
# Fuente: NOAA — valores del índice ONI por año
# > +0.5 = El Niño, < -0.5 = La Niña, entre = Neutro

ENSO_HISTORICO = {
    2007: {"fase": "La Nina",  "intensidad": "moderada", "oni": -1.2},
    2008: {"fase": "La Nina",  "intensidad": "moderada", "oni": -0.8},
    2009: {"fase": "El Nino",  "intensidad": "moderada", "oni": 0.9},
    2010: {"fase": "La Nina",  "intensidad": "fuerte",   "oni": -1.5},
    2011: {"fase": "La Nina",  "intensidad": "moderada", "oni": -1.0},
    2012: {"fase": "Neutro",   "intensidad": "neutro",   "oni": 0.2},
    2013: {"fase": "Neutro",   "intensidad": "neutro",   "oni": 0.1},
    2014: {"fase": "El Nino",  "intensidad": "debil",    "oni": 0.6},
    2015: {"fase": "El Nino",  "intensidad": "fuerte",   "oni": 2.3},
    2016: {"fase": "La Nina",  "intensidad": "debil",    "oni": -0.7},
    2017: {"fase": "La Nina",  "intensidad": "debil",    "oni": -0.8},
    2018: {"fase": "El Nino",  "intensidad": "debil",    "oni": 0.8},
    2019: {"fase": "El Nino",  "intensidad": "debil",    "oni": 0.5},
    2020: {"fase": "La Nina",  "intensidad": "moderada", "oni": -1.2},
    2021: {"fase": "La Nina",  "intensidad": "moderada", "oni": -1.0},
    2022: {"fase": "La Nina",  "intensidad": "moderada", "oni": -0.9},
    2023: {"fase": "El Nino",  "intensidad": "fuerte",   "oni": 2.0},
    2024: {"fase": "La Nina",  "intensidad": "debil",    "oni": -0.6},
}

# ── 1. Fetch EVA completo ─────────────────────────────────

async def fetch_eva_completo(max_registros: int = 50000) -> pd.DataFrame:
    """Descarga todos los registros EVA disponibles."""
    url = "https://www.datos.gov.co/resource/uejq-wxrr.json"
    all_data = []

    logger.info("Descargando EVA 2019-2024...")
    async with httpx.AsyncClient(timeout=60) as client:
        for offset in range(0, max_registros, 1000):
            params = {
                "$limit": 1000,
                "$offset": offset,
                "$order": "a_o DESC",
                "$where": "rendimiento IS NOT NULL AND rea_sembrada IS NOT NULL",
            }
            try:
                r = await client.get(url, params=params)
                batch = r.json()
                if not batch:
                    break
                all_data.extend(batch)
                if offset % 5000 == 0:
                    logger.info(f"  EVA: {len(all_data)} registros descargados...")
            except Exception as e:
                logger.error(f"Error offset {offset}: {e}")
                break

    df = pd.DataFrame(all_data)
    logger.info(f"EVA total: {len(df)} registros")
    return df


# ── 2. Limpiar EVA ────────────────────────────────────────

def limpiar_eva(df: pd.DataFrame) -> pd.DataFrame:
    """Limpieza y normalización del dataset EVA."""

    # Renombrar columnas
    rename = {
        "c_digo_dane_departamento": "codigo_dpto",
        "c_digo_dane_municipio":    "codigo_mpio",
        "a_o":                      "anio",
        "rea_sembrada":             "area_sembrada",
        "rea_cosechada":            "area_cosechada",
        "producci_n":               "produccion",
        "grupo_cultivo":            "grupo_cultivo",
        "desagregaci_n_cultivo":    "desagregacion",
        "ciclo_del_cultivo":        "ciclo",
        "estado_f_sico_del_cultivo":"estado_fisico",
        "c_digo_del_cultivo":       "codigo_cultivo",
        "nombre_cient_fico_del_cultivo": "nombre_cientifico",
    }
    df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})

    # Normalizar texto
    for col in ["departamento", "municipio", "cultivo", "grupo_cultivo"]:
        if col in df.columns:
            df[col] = df[col].str.upper().str.strip()
            df[col] = df[col].str.normalize("NFKD").str.encode("ascii", errors="ignore").str.decode("ascii")

    # Convertir numéricos
    for col in ["area_sembrada", "area_cosechada", "produccion", "rendimiento"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["anio"] = pd.to_numeric(df["anio"], errors="coerce").astype("Int64")

    # Parsear periodo
    def parse_periodo(p):
        if pd.isna(p): return 0
        p = str(p).upper()
        if "PRIMER" in p or "1" in p: return 1
        if "SEGUNDO" in p or "2" in p: return 2
        return 0

    if "periodo" in df.columns:
        df["semestre"] = df["periodo"].apply(parse_periodo)

    # Filtros de calidad
    df = df.dropna(subset=["departamento", "cultivo", "anio", "rendimiento"])
    df = df[df["rendimiento"] > 0]
    df = df[df["rendimiento"] < 200]      # Outliers extremos
    df = df[df["area_sembrada"] > 0]
    df = df[df["anio"] >= 2007]

    # Eliminar duplicados
    df = df.drop_duplicates(
        subset=["departamento", "municipio", "cultivo", "anio", "semestre"],
        keep="last"
    )

    logger.info(f"EVA limpio: {len(df)} registros")
    return df.reset_index(drop=True)


# ── 3. Fetch clima anual NASA POWER ──────────────────────

async def fetch_clima_anual(departamento: str, anio: int, lat: float, lng: float) -> dict:
    """Clima promedio anual para un departamento y año."""
    url = "https://power.larc.nasa.gov/api/temporal/annual/point"
    params = {
        "parameters": "T2M,PRECTOTCORR,RH2M,ALLSKY_SFC_SW_DWN",
        "community": "AG",
        "longitude": lng,
        "latitude": lat,
        "start": anio,
        "end": anio,
        "format": "JSON",
    }
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.get(url, params=params)
            data = r.json()
        props = data.get("properties", {}).get("parameter", {})
        return {
            "departamento": departamento,
            "anio": anio,
            "temp_promedio":  list(props.get("T2M", {}).values())[0] if props.get("T2M") else None,
            "precipitacion":  list(props.get("PRECTOTCORR", {}).values())[0] if props.get("PRECTOTCORR") else None,
            "humedad":        list(props.get("RH2M", {}).values())[0] if props.get("RH2M") else None,
            "radiacion_solar":list(props.get("ALLSKY_SFC_SW_DWN", {}).values())[0] if props.get("ALLSKY_SFC_SW_DWN") else None,
        }
    except Exception as e:
        logger.error(f"NASA POWER error {departamento} {anio}: {e}")
        return {"departamento": departamento, "anio": anio}


async def construir_clima_historico(anios: list) -> pd.DataFrame:
    """Construye tabla de clima histórico para todos los departamentos y años."""
    semaphore = asyncio.Semaphore(5)
    tasks = []

    async def fetch_one(dept, anio, lat, lng):
        async with semaphore:
            return await fetch_clima_anual(dept, anio, lat, lng)

    for dept, info in DEPARTAMENTOS_GEO.items():
        for anio in anios:
            tasks.append(fetch_one(dept, anio, info["lat"], info["lng"]))

    logger.info(f"Descargando clima para {len(tasks)} combinaciones dept/año...")
    results = await asyncio.gather(*tasks, return_exceptions=True)

    rows = [r for r in results if isinstance(r, dict) and "temp_promedio" in r]
    df = pd.DataFrame(rows)
    logger.info(f"Clima histórico: {len(df)} registros")
    return df


# ── 4. Integrar ENSO ─────────────────────────────────────

def agregar_enso(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega variables ENSO al dataset."""
    enso_df = pd.DataFrame([
        {
            "anio": anio,
            "enso_fase": v["fase"],
            "enso_intensidad": v["intensidad"],
            "oni_index": v["oni"],
            "es_el_nino": 1 if v["fase"] == "El Nino" else 0,
            "es_la_nina": 1 if v["fase"] == "La Nina" else 0,
        }
        for anio, v in ENSO_HISTORICO.items()
    ])
    df["anio"] = df["anio"].astype(int)
    enso_df["anio"] = enso_df["anio"].astype(int)
    return df.merge(enso_df, on="anio", how="left")


# ── 5. Feature Engineering ────────────────────────────────

def feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    """Crea variables derivadas para mejorar el modelo."""

    # Rendimiento promedio histórico por cultivo/departamento
    rend_hist = df.groupby(["departamento", "cultivo"])["rendimiento"].mean().reset_index()
    rend_hist.columns = ["departamento", "cultivo", "rendimiento_hist_promedio"]
    df = df.merge(rend_hist, on=["departamento", "cultivo"], how="left")

    # Desviación del rendimiento respecto al promedio histórico
    df["rendimiento_vs_historico"] = df["rendimiento"] - df["rendimiento_hist_promedio"]

    # Ratio área cosechada vs sembrada (eficiencia)
    if "area_cosechada" in df.columns and "area_sembrada" in df.columns:
        df["ratio_cosecha"] = (df["area_cosechada"] / df["area_sembrada"]).clip(0, 1)

    # Impacto ENSO en rendimiento (diferencia media con/sin evento)
    if "es_el_nino" in df.columns:
        rend_nino  = df[df["es_el_nino"] == 1].groupby(["departamento","cultivo"])["rendimiento"].mean()
        rend_normal = df[df["es_el_nino"] == 0].groupby(["departamento","cultivo"])["rendimiento"].mean()
        impacto = (rend_nino - rend_normal).reset_index()
        impacto.columns = ["departamento", "cultivo", "impacto_el_nino"]
        df = df.merge(impacto, on=["departamento","cultivo"], how="left")

    # Categorías de riesgo climático
    if "oni_index" in df.columns:
        df["riesgo_climatico"] = pd.cut(
            df["oni_index"],
            bins=[-float("inf"), -1.5, -0.5, 0.5, 1.5, float("inf")],
            labels=["la_nina_fuerte", "la_nina", "neutro", "el_nino", "el_nino_fuerte"]
        )

    return df


# ── 6. Pipeline completo ──────────────────────────────────

async def construir_dataset_maestro(max_eva: int = 30000) -> dict:
    """
    Pipeline ETL completo.
    Construye el dataset maestro y lo guarda en datasets/features/
    """
    inicio = datetime.utcnow()
    logger.info("=== INICIANDO ETL PIPELINE ===")

    # 1. EVA
    eva_raw = await fetch_eva_completo(max_eva)
    eva_raw.to_csv(f"{RAW_PATH}/eva_raw.csv", index=False)

    # 2. Limpiar
    eva_clean = limpiar_eva(eva_raw)
    eva_clean.to_csv(f"{PROCESSED_PATH}/eva_clean.csv", index=False)

    # 3. Clima histórico (solo años del EVA)
    anios = sorted(eva_clean["anio"].dropna().unique().tolist())
    anios_int = [int(a) for a in anios if 2007 <= int(a) <= 2024]

    clima = await construir_clima_historico(anios_int[:5])  # Limitar para demo
    clima.to_csv(f"{PROCESSED_PATH}/clima_historico.csv", index=False)

    # 4. Merge EVA + Clima
    eva_clean["anio"] = eva_clean["anio"].astype(int)
    clima["anio"] = clima["anio"].astype(int)
    merged = eva_clean.merge(clima, on=["departamento", "anio"], how="left")

    # 5. ENSO
    merged = agregar_enso(merged)

    # 6. Feature engineering
    dataset_final = feature_engineering(merged)

    # 7. Guardar
    dataset_final.to_csv(f"{FEATURES_PATH}/dataset_maestro.csv", index=False)

    duracion = (datetime.utcnow() - inicio).seconds

    stats = {
        "success": True,
        "duracion_segundos": duracion,
        "registros_eva_raw": len(eva_raw),
        "registros_eva_clean": len(eva_clean),
        "registros_dataset_final": len(dataset_final),
        "departamentos": dataset_final["departamento"].nunique(),
        "cultivos": dataset_final["cultivo"].nunique(),
        "anios": sorted(dataset_final["anio"].unique().tolist()),
        "columnas": list(dataset_final.columns),
        "archivos": {
            "raw":      f"{RAW_PATH}/eva_raw.csv",
            "clean":    f"{PROCESSED_PATH}/eva_clean.csv",
            "clima":    f"{PROCESSED_PATH}/clima_historico.csv",
            "maestro":  f"{FEATURES_PATH}/dataset_maestro.csv",
        }
    }

    logger.info(f"=== ETL COMPLETADO en {duracion}s ===")
    logger.info(f"Dataset maestro: {len(dataset_final)} registros")
    return stats
