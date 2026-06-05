"""
AgroVision AI — Limpieza general de datasets (datos.gov.co / SODA2).
Orientada a preparar datos para entrenamiento de modelos ML.

Pasos:
  1. reporte_calidad()          → métricas de calidad por columna
  2. eliminar_cols_irrelevantes() → URLs, IDs, alto % nulos, constantes
  3. tratar_nulos()             → mediana / moda / DESCONOCIDO
  4. eliminar_duplicados()      → keep='first', guarda los eliminados
  5. convertir_tipos()          → fechas → features, strings → numérico
  6. tratar_outliers()          → IQR Winsorizing / Z-score / eliminar
  7. encode_categoricas()       → OneHot ≤N únicos, Label >N únicos
  8. escalar_numericas()        → StandardScaler / MinMaxScaler / none
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Literal

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.preprocessing import LabelEncoder, MinMaxScaler, StandardScaler

from app.config.constants import LIMPIEZA

logger = logging.getLogger(__name__)

# ── Tipos ─────────────────────────────────────────────────

MetodoOutliers = Literal["iqr", "zscore", "eliminar"]
MetodoEncoding = Literal["auto", "label", "onehot"]
MetodoEscalado = Literal["standard", "minmax", "none"]


# ── 1. Reporte de calidad ─────────────────────────────────

def reporte_calidad(df: pd.DataFrame) -> pd.DataFrame:
    """
    Genera un DataFrame con métricas de calidad por columna.
    Retorna el reporte como DataFrame (puede guardarse como CSV).
    """
    reporte = pd.DataFrame({
        "dtype":      df.dtypes,
        "nulos":      df.isnull().sum(),
        "pct_nulos":  (df.isnull().sum() / len(df) * 100).round(2),
        "unicos":     df.nunique(),
        "pct_unicos": (df.nunique() / len(df) * 100).round(2),
        "ejemplo":    df.apply(lambda c: c.dropna().iloc[0] if c.dropna().size else None),
    })

    duplicados    = df.duplicated().sum()
    pct_dup       = duplicados / len(df) * 100

    logger.info(
        "Calidad — filas: %d | cols: %d | duplicados: %d (%.1f%%) | nulos totales: %d",
        df.shape[0], df.shape[1], duplicados, pct_dup, df.isnull().sum().sum(),
    )
    return reporte


# ── 2. Columnas irrelevantes ──────────────────────────────

def eliminar_cols_irrelevantes(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """
    Elimina:
      a) Columnas definidas como siempre irrelevantes en LIMPIEZA config
      b) Columnas con más de UMBRAL_NULOS_COLS de nulos
      c) Columnas constantes (1 único valor)
      d) Columnas ID-puro (cardinalidad ≥ 95% de filas, tipo object)
    Retorna (df_limpio, lista_columnas_eliminadas).
    """
    eliminadas: list[str] = []
    umbral      = LIMPIEZA["umbral_nulos_cols"]
    cols_fijas  = LIMPIEZA["cols_siempre_eliminar"]

    # a) Siempre eliminar
    drop = [c for c in cols_fijas if c in df.columns]
    df   = df.drop(columns=drop)
    eliminadas.extend(drop)
    logger.info("[cols] Fijas eliminadas (%d): %s", len(drop), drop)

    # b) Alto % de nulos
    pct_nulos   = df.isnull().mean()
    drop_nulos  = pct_nulos[pct_nulos > umbral].index.tolist()
    df          = df.drop(columns=drop_nulos)
    eliminadas.extend(drop_nulos)
    logger.info("[cols] >%.0f%% nulos eliminadas (%d): %s",
                umbral * 100, len(drop_nulos), drop_nulos)

    # c) Constantes
    drop_const = [c for c in df.columns if df[c].nunique() <= 1]
    df         = df.drop(columns=drop_const)
    eliminadas.extend(drop_const)
    logger.info("[cols] Constantes eliminadas (%d): %s", len(drop_const), drop_const)

    # d) ID-puro (cardinalidad casi 100%)
    drop_id = [
        c for c in df.columns
        if df[c].dtype == object and df[c].nunique() / len(df) > 0.95
    ]
    df = df.drop(columns=drop_id)
    eliminadas.extend(drop_id)
    logger.info("[cols] ID-puro eliminadas (%d): %s", len(drop_id), drop_id)

    return df, eliminadas


# ── 3. Tratamiento de nulos ───────────────────────────────

def tratar_nulos(df: pd.DataFrame) -> pd.DataFrame:
    """
    Por tipo de columna:
      - bool      → False
      - numérico  → mediana (robusta a outliers)
      - object    → moda; si vacía → 'DESCONOCIDO'
    Primero elimina filas con demasiados nulos.
    """
    umbral_filas = LIMPIEZA["umbral_nulos_filas"]
    thresh       = int((1 - umbral_filas) * df.shape[1])

    antes = len(df)
    df    = df.dropna(thresh=thresh)
    logger.info("[nulos] Filas eliminadas por exceso de nulos: %d", antes - len(df))

    for col in df.columns:
        n = df[col].isnull().sum()
        if n == 0:
            continue

        if df[col].dtype == bool:
            df[col] = df[col].fillna(False)

        elif pd.api.types.is_numeric_dtype(df[col]):
            mediana = df[col].median()
            df[col] = df[col].fillna(mediana)
            logger.debug("[nulos] %s: %d nulos → mediana (%.4f)", col, n, mediana)

        else:
            moda  = df[col].mode()
            valor = moda.iloc[0] if not moda.empty else "DESCONOCIDO"
            df[col] = df[col].fillna(valor)
            logger.debug("[nulos] %s: %d nulos → moda ('%s')", col, n, valor)

    logger.info("[nulos] Nulos restantes: %d", df.isnull().sum().sum())
    return df


# ── 4. Duplicados ─────────────────────────────────────────

def eliminar_duplicados(
    df: pd.DataFrame,
    ruta_auditoria: Path | None = None,
) -> pd.DataFrame:
    """
    Elimina filas completamente duplicadas (keep='first').
    Si se pasa ruta_auditoria, guarda los duplicados en CSV para revisión.
    """
    duplicados = df[df.duplicated(keep=False)].copy()
    antes      = len(df)

    if not duplicados.empty and ruta_auditoria:
        ruta_auditoria.parent.mkdir(parents=True, exist_ok=True)
        duplicados.to_csv(ruta_auditoria, index=False)
        logger.info("[dup] %d filas duplicadas guardadas en %s",
                    len(duplicados), ruta_auditoria)

    df = df.drop_duplicates(keep="first")
    logger.info("[dup] Duplicados eliminados: %d | Filas restantes: %d",
                antes - len(df), len(df))
    return df


# ── 5. Conversión de tipos ────────────────────────────────

def convertir_tipos(df: pd.DataFrame) -> pd.DataFrame:
    """
    - Fechas   → datetime; extrae año, mes, día_semana como features
    - Strings numéricos → float64
    """
    cols_fecha   = LIMPIEZA["cols_fecha"]
    cols_num_str = LIMPIEZA["cols_numericas_string"]

    for col in cols_fecha:
        if col not in df.columns:
            continue
        df[col] = pd.to_datetime(df[col], errors="coerce")
        df[f"{col}_anio"]       = df[col].dt.year
        df[f"{col}_mes"]        = df[col].dt.month
        df[f"{col}_dia_semana"] = df[col].dt.dayofweek
        df = df.drop(columns=[col])
        logger.info("[tipos] %s → 3 features temporales", col)

    for col in cols_num_str:
        if col not in df.columns:
            continue
        df[col] = pd.to_numeric(df[col], errors="coerce")
        logger.info("[tipos] %s → float64", col)

    return df


# ── 6. Outliers ───────────────────────────────────────────

def tratar_outliers(
    df: pd.DataFrame,
    metodo: MetodoOutliers = "iqr",
) -> pd.DataFrame:
    """
    Detecta y trata outliers en columnas numéricas.

    - 'iqr'      → Winsorizing en [Q1 - k*IQR, Q3 + k*IQR] (conserva filas)
    - 'zscore'   → Reemplaza por mediana si |z| > umbral
    - 'eliminar' → Elimina filas con |z| > umbral
    """
    iqr_mult      = LIMPIEZA["iqr_mult"]
    zscore_umbral = LIMPIEZA["zscore_umbral"]
    numericas     = df.select_dtypes(include=np.number).columns.tolist()

    for col in numericas:
        serie = df[col].dropna()
        if len(serie) < 10:
            continue

        if metodo == "iqr":
            Q1      = serie.quantile(0.25)
            Q3      = serie.quantile(0.75)
            IQR     = Q3 - Q1
            lim_inf = Q1 - iqr_mult * IQR
            lim_sup = Q3 + iqr_mult * IQR
            n_out   = int(((df[col] < lim_inf) | (df[col] > lim_sup)).sum())
            if n_out:
                df[col] = df[col].clip(lower=lim_inf, upper=lim_sup)
                logger.debug("[outliers] %s: %d Winsorized [%.2f, %.2f]",
                             col, n_out, lim_inf, lim_sup)

        elif metodo == "zscore":
            z    = np.abs(stats.zscore(serie))
            mask = z > zscore_umbral
            n_out = int(mask.sum())
            if n_out:
                mediana = df[col].median()
                df.loc[df.index.isin(serie[mask].index), col] = mediana
                logger.debug("[outliers] %s: %d → mediana (z>%.1f)",
                             col, n_out, zscore_umbral)

        elif metodo == "eliminar":
            z     = np.abs(stats.zscore(serie))
            mask  = z > zscore_umbral
            antes = len(df)
            df    = df[~df.index.isin(serie[mask].index)]
            logger.debug("[outliers] %s: %d filas eliminadas",
                         col, antes - len(df))

    logger.info("[outliers] Método '%s' aplicado sobre %d columnas numéricas",
                metodo, len(numericas))
    return df


# ── 7. Encoding categórico ────────────────────────────────

def encode_categoricas(
    df: pd.DataFrame,
    estrategia: MetodoEncoding = "auto",
    ruta_encoders: Path | None = None,
) -> pd.DataFrame:
    """
    - Binarias / baja cardinalidad (≤ max_cardinalidad_onehot) → One-Hot
    - Alta cardinalidad                                         → Label Encoding
    Guarda el mapa de encoders en JSON para poder invertir en producción.
    """
    max_card  = LIMPIEZA["max_cardinalidad_onehot"]
    cat_cols  = df.select_dtypes(include="object").columns.tolist()
    encoders  = {}

    for col in cat_cols:
        n = df[col].nunique()
        usar_onehot = (
            estrategia == "onehot"
            or (estrategia == "auto" and n <= max_card)
        )

        if usar_onehot and estrategia != "label":
            dummies = pd.get_dummies(df[col], prefix=col, drop_first=True, dtype=int)
            df      = pd.concat([df.drop(columns=[col]), dummies], axis=1)
            encoders[col] = {"tipo": "onehot", "columnas": list(dummies.columns)}
            logger.debug("[enc] %s (%d únicos) → One-Hot (%d cols)", col, n, dummies.shape[1])
        else:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            encoders[col] = {"tipo": "label", "clases": list(le.classes_)}
            logger.debug("[enc] %s (%d únicos) → Label", col, n)

    if ruta_encoders:
        ruta_encoders.parent.mkdir(parents=True, exist_ok=True)
        with open(ruta_encoders, "w", encoding="utf-8") as f:
            json.dump(encoders, f, ensure_ascii=False, indent=2)
        logger.info("[enc] Mapa encoders guardado en %s", ruta_encoders)

    logger.info("[enc] %d columnas categóricas procesadas", len(cat_cols))
    return df


# ── 8. Escalado numérico ──────────────────────────────────

def escalar_numericas(
    df: pd.DataFrame,
    metodo: MetodoEscalado = "none",
) -> pd.DataFrame:
    """
    - 'standard' → StandardScaler (media=0, std=1) — SVM, regresión, redes
    - 'minmax'   → MinMaxScaler (0 a 1)             — redes neuronales, KNN
    - 'none'     → sin escalado (árboles, RF, XGBoost no lo necesitan)
    """
    if metodo == "none":
        logger.info("[escala] Escalado omitido")
        return df

    numericas = df.select_dtypes(include=np.number).columns.tolist()
    scaler    = StandardScaler() if metodo == "standard" else MinMaxScaler()
    df[numericas] = scaler.fit_transform(df[numericas])
    logger.info("[escala] %s aplicado a %d columnas", metodo, len(numericas))
    return df