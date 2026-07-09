"""AgroVision AI — Pipeline ETL maestro."""
# Copyright (C) 2026 July Mayerly Quintero Farfán

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

import pandas as pd

from app.config.constants import DEPARTAMENTOS, ENSO_HISTORICO
from app.etl.cleaners.eva_cleaner import clean_eva
from app.etl.transformers.enso_transformer import add_enso
from app.infrastructure.clients.eva_client import EvaClient
from app.infrastructure.clients.nasa_client import NasaClient
from app.infrastructure.persistence.dataset_storage import DatasetStorage

logger = logging.getLogger(__name__)


def feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    """Crea variables derivadas para el modelo ML."""
    df = df.copy()

    # Rendimiento histórico promedio por cultivo/departamento
    hist = (
        df.groupby(["departamento", "cultivo"])["rendimiento"]
        .mean()
        .reset_index()
        .rename(columns={"rendimiento": "rendimiento_hist_promedio"})
    )
    df = df.merge(hist, on=["departamento", "cultivo"], how="left")
    df["rendimiento_vs_historico"] = df["rendimiento"] - df["rendimiento_hist_promedio"]

    # Ratio área cosechada/sembrada
    if "area_cosechada" in df.columns and "area_sembrada" in df.columns:
        df["ratio_cosecha"] = (df["area_cosechada"] / df["area_sembrada"]).clip(0, 1)

    # Impacto El Niño en rendimiento
    if "es_el_nino" in df.columns:
        nino   = df[df["es_el_nino"] == 1].groupby(["departamento", "cultivo"])["rendimiento"].mean()
        normal = df[df["es_el_nino"] == 0].groupby(["departamento", "cultivo"])["rendimiento"].mean()
        impacto = (nino - normal).reset_index().rename(columns={"rendimiento": "impacto_el_nino"})
        df = df.merge(impacto, on=["departamento", "cultivo"], how="left")

    # Categoría de riesgo climático
    if "oni_index" in df.columns:
        df["riesgo_climatico"] = pd.cut(
            df["oni_index"],
            bins=[-float("inf"), -1.5, -0.5, 0.5, 1.5, float("inf")],
            labels=["la_nina_fuerte", "la_nina", "neutro", "el_nino", "el_nino_fuerte"],
        )

    return df


async def _fetch_clima_anual_all(anios: list[int]) -> pd.DataFrame:
    nasa = NasaClient()
    semaphore = asyncio.Semaphore(5)

    async def one(dept: str, info: dict, anio: int) -> dict:
        async with semaphore:
            return await nasa.fetch_annual(info["lat"], info["lng"], anio, dept)

    tasks = [
        one(dept, info, anio)
        for dept, info in DEPARTAMENTOS.items()
        for anio in anios
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    rows = [r for r in results if isinstance(r, dict) and r.get("temp_promedio") is not None]
    if not rows:
        logger.warning("NASA POWER devolvió 0 registros válidos")
        return pd.DataFrame(columns=["departamento", "anio",
                                     "temp_promedio", "precipitacion",
                                     "humedad", "radiacion_solar"])
    return pd.DataFrame(rows)   # BUG ORIGINAL CORREGIDO: return faltante


async def run_master_pipeline(max_eva: int = 30000) -> dict:
    """Pipeline ETL completo: EVA → limpiar → clima → ENSO → features → guardar."""
    inicio = datetime.now(timezone.utc)
    logger.info("=== INICIANDO ETL PIPELINE ===")

    # 1. Descargar EVA
    eva_client = EvaClient()
    eva_raw = await eva_client.fetch_paginated(limit=max_eva)
    DatasetStorage.save_raw(eva_raw, "eva_raw")

    # 2. Limpiar
    eva_clean = clean_eva(eva_raw)
    DatasetStorage.save_processed(eva_clean, "eva_clean")

    # 3. Clima histórico
    anios = sorted({int(a) for a in eva_clean["anio"].dropna() if 2007 <= int(a) <= 2024})
    clima = await _fetch_clima_anual_all(anios[:5])   # limitado para demo
    DatasetStorage.save_processed(clima, "clima_historico")

    # 4. Merge EVA + clima
    eva_clean["anio"] = eva_clean["anio"].astype(int)
    if not clima.empty and "anio" in clima.columns:
        clima["anio"] = clima["anio"].astype(int)
        merged = eva_clean.merge(clima, on=["departamento", "anio"], how="left")
    else:
        logger.warning("Clima vacío — continuando sin variables climáticas")
        merged = eva_clean.copy()

    # 5. ENSO + feature engineering
    merged  = add_enso(merged)
    dataset = feature_engineering(merged)

    # 6. Guardar dataset maestro
    DatasetStorage.save_features(dataset, "dataset_maestro")

    duracion = (datetime.now(timezone.utc) - inicio).seconds
    logger.info("=== ETL COMPLETADO en %ds ===", duracion)

    return {
        "success":                  True,
        "duracion_segundos":        duracion,
        "registros_eva_raw":        len(eva_raw),
        "registros_eva_clean":      len(eva_clean),
        "registros_dataset_final":  len(dataset),
        "departamentos":            dataset["departamento"].nunique() if "departamento" in dataset.columns else 0,
        "cultivos":                 dataset["cultivo"].nunique() if "cultivo" in dataset.columns else 0,
        "columnas":                 list(dataset.columns),
    }
