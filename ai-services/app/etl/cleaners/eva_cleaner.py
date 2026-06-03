"""AgroVision AI — Limpieza del dataset EVA."""
from __future__ import annotations

import logging

import pandas as pd

logger = logging.getLogger(__name__)

_RENAME: dict[str, str] = {
    "c_digo_dane_departamento":      "codigo_dpto",
    "c_digo_dane_municipio":         "codigo_mpio",
    "a_o":                           "anio",
    "rea_sembrada":                  "area_sembrada",
    "rea_cosechada":                 "area_cosechada",
    "producci_n":                    "produccion",
    "grupo_cultivo":                 "grupo_cultivo",
    "desagregaci_n_cultivo":         "desagregacion",
    "ciclo_del_cultivo":             "ciclo",
    "estado_f_sico_del_cultivo":     "estado_fisico",
    "c_digo_del_cultivo":            "codigo_cultivo",
    "nombre_cient_fico_del_cultivo": "nombre_cientifico",
}


def _parse_periodo(p: object) -> int:
    if pd.isna(p):
        return 0
    s = str(p).upper()
    if "PRIMER" in s or s.startswith("1"):
        return 1
    if "SEGUNDO" in s or s.startswith("2"):
        return 2
    return 0


def clean_eva(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpieza y normalización completa del dataset EVA.
    Retorna un DataFrame listo para el pipeline ETL.
    """
    df = df.copy()

    # Renombrar columnas con caracteres especiales
    df = df.rename(columns={k: v for k, v in _RENAME.items() if k in df.columns})

    # Normalizar texto — fillna PRIMERO para evitar AttributeError en str ops
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

    # Convertir numéricos
    for col in ["area_sembrada", "area_cosechada", "produccion", "rendimiento"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["anio"] = pd.to_numeric(df.get("anio", pd.Series(dtype=float)), errors="coerce").astype("Int64")

    if "periodo" in df.columns:
        df["semestre"] = df["periodo"].apply(_parse_periodo)

    # Filtros de calidad
    df = df.dropna(subset=["departamento", "cultivo", "anio", "rendimiento"])
    df = df[df["rendimiento"] > 0]
    df = df[df["rendimiento"] < 50]       # máximo realista Colombia (t/ha)
    df = df[df["area_sembrada"].fillna(0) > 0]
    df = df[df["anio"] >= 2007]

    # Eliminar duplicados
    dup_cols = [c for c in ["departamento", "municipio", "cultivo", "anio", "semestre"] if c in df.columns]
    df = df.drop_duplicates(subset=dup_cols, keep="last")

    logger.info("EVA limpio: %d registros", len(df))
    return df.reset_index(drop=True)
