"""
AgroVision AI — Feature engineering para el modelo ML.

NOTA: El renombrado de columnas EVA (a_o → anio, rea_sembrada → area_sembrada, etc.)
ocurre en EvaClient._normalizar_df(). Este módulo asume columnas ya canónicas.
"""
from __future__ import annotations

import logging

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder

from app.utils.dates import parse_periodo

logger = logging.getLogger(__name__)

# Columnas categóricas que se encodean
CAT_COLS = ["departamento", "cultivo", "grupo_cultivo"]

# Features finales que consume el modelo
FEATURE_COLS = [
    "departamento_enc",
    "cultivo_enc",
    "grupo_cultivo_enc",
    "area_sembrada",
    "anio",
    "periodo_num",
]


def prepare_features(
    df: pd.DataFrame,
    encoders: dict | None = None,
    fit: bool = True,
) -> tuple[pd.DataFrame, pd.Series | None, dict]:
    """
    Prepara el DataFrame EVA para entrenamiento o inferencia.

    El DataFrame de entrada debe venir con columnas canónicas
    (ya procesado por EvaClient o por el ETL cleaner):
        anio, area_sembrada, area_cosechada, produccion, rendimiento,
        departamento, cultivo, grupo_cultivo, periodo / semestre

    Parámetros:
        df       : DataFrame con columnas canónicas
        encoders : LabelEncoders ya entrenados (None = crear nuevos en fit=True)
        fit      : True → entrenamiento, False → inferencia

    Retorna:
        X        : DataFrame con las FEATURE_COLS listas para el modelo
        y        : Serie 'rendimiento' (target) o None si no existe
        encoders : dict de LabelEncoders por columna categórica
    """
    df = df.copy()

    # ── Numéricos (por si alguno llegó como string) ───────
    for col in ["area_sembrada", "area_cosechada", "produccion", "rendimiento", "anio"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # ── Periodo → entero ──────────────────────────────────
    if "periodo" in df.columns:
        df["periodo_num"] = df["periodo"].apply(parse_periodo)
    elif "semestre" in df.columns:
        # El cleaner ya lo convirtió como 'semestre'
        df["periodo_num"] = df["semestre"]
    elif "periodo_num" not in df.columns:
        df["periodo_num"] = 0

    # ── Filtros de calidad (solo entrenamiento) ───────────
    if fit and "rendimiento" in df.columns:
        df = df.dropna(subset=["rendimiento"])
        df = df[df["rendimiento"] > 0]
        df = df[df["rendimiento"] < 50]   # máximo realista Colombia

    df = df.dropna(subset=["area_sembrada", "anio"])
    df = df[df["area_sembrada"].fillna(0) > 0]

    # ── Encoding categórico ───────────────────────────────
    if encoders is None:
        encoders = {}

    for col in CAT_COLS:
        if col not in df.columns:
            df[col] = "DESCONOCIDO"

        df[col] = df[col].fillna("DESCONOCIDO").str.upper().str.strip()

        if fit:
            enc = LabelEncoder()
            df[f"{col}_enc"] = enc.fit_transform(df[col])
            encoders[col] = enc
        else:
            enc = encoders.get(col)
            if enc:
                known = set(enc.classes_)
                df[col] = df[col].apply(lambda x: x if x in known else "DESCONOCIDO")
                if "DESCONOCIDO" not in enc.classes_:
                    enc.classes_ = np.append(enc.classes_, "DESCONOCIDO")
                df[f"{col}_enc"] = enc.transform(df[col])
            else:
                df[f"{col}_enc"] = 0

    # ── Asegurar que todas las features existen ───────────
    for col in FEATURE_COLS:
        if col not in df.columns:
            df[col] = 0

    y = df["rendimiento"] if "rendimiento" in df.columns else None
    return df[FEATURE_COLS].copy(), y, encoders


def domain_feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrega variables derivadas de dominio al dataset maestro ETL.
    Opera sobre el dataset completo (no por fila).
    """
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

    # Ratio área cosechada vs sembrada
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