"""
AgroVision AI — Limpieza del dataset EVA.

NOTA: el renombrado de columnas (a_o → anio, rea_sembrada → area_sembrada, etc.)
se hace en EvaClient._normalizar_df() antes de llegar aquí.
Este módulo asume que el DataFrame ya viene con los nombres canónicos.
"""
# Copyright (C) 2026 July Mayerly Quintero Farfán

from __future__ import annotations

import logging

import pandas as pd

logger = logging.getLogger(__name__)


def _parse_periodo(p: object) -> int:
    if pd.isna(p):
        return 0
    s = str(p).upper()
    if "PRIMER" in s or s.strip().startswith("1"):
        return 1
    if "SEGUNDO" in s or s.strip().startswith("2"):
        return 2
    return 0


def clean_eva(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpieza y normalización del dataset EVA.
    Asume que EvaClient ya aplicó _normalizar_df() al DataFrame:
      - Columnas renombradas (a_o → anio, rea_sembrada → area_sembrada, etc.)
      - Tipos numéricos ya convertidos con pd.to_numeric

    Pasos que aplica este cleaner:
      1. Normalizar texto (mayúsculas, sin tildes)
      2. Parsear periodo → semestre (0 / 1 / 2)
      3. Filtros de calidad (outliers, nulos, duplicados)
    """
    df = df.copy()

    # ── 1. Normalizar texto ───────────────────────────────
    # fillna("") PRIMERO para evitar AttributeError en str ops
    for col in ["departamento", "municipio", "cultivo", "grupo_cultivo"]:
        if col in df.columns:
            df[col] = (
                df[col]
                .fillna("")
                .str.strip()
                .str.upper()
                .str.normalize("NFKD")
                .str.encode("ascii", errors="ignore")
                .str.decode("ascii")
            )

    # ── 2. Semestre ───────────────────────────────────────
    if "periodo" in df.columns:
        df["semestre"] = df["periodo"].apply(_parse_periodo)
    elif "semestre" not in df.columns:
        df["semestre"] = 0

    # ── 3. Conversión anio (por si llega como float) ──────
    if "anio" in df.columns:
        df["anio"] = pd.to_numeric(df["anio"], errors="coerce").astype("Int64")

    # ── 4. Filtros de calidad ─────────────────────────────
    df = df.dropna(subset=["departamento", "cultivo", "anio", "rendimiento"])
    df = df[df["rendimiento"] > 0]
    df = df[df["rendimiento"] < 50]        # máximo realista Colombia (t/ha)

    if "area_sembrada" in df.columns:
        df = df[df["area_sembrada"].fillna(0) > 0]

    df = df[df["anio"] >= 2007]

    # ── 5. Eliminar duplicados ────────────────────────────
    dup_cols = [
        c for c in ["departamento", "municipio", "cultivo", "anio", "semestre"]
        if c in df.columns
    ]
    df = df.drop_duplicates(subset=dup_cols, keep="last")

    logger.info("EVA limpio: %d registros", len(df))
    return df.reset_index(drop=True)