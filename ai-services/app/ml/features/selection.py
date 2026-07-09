"""AgroVision AI — Selección de features."""
# Copyright (C) 2026 July Mayerly Quintero Farfán

from __future__ import annotations

import logging

import pandas as pd

from .engineering import FEATURE_COLS

logger = logging.getLogger(__name__)


def get_feature_importance(model, feature_names: list[str] | None = None) -> dict[str, float]:
    """Extrae importancia de features de un modelo sklearn."""
    names = feature_names or FEATURE_COLS
    if not hasattr(model, "feature_importances_"):
        return {}
    return {
        name: round(float(imp), 4)
        for name, imp in zip(names, model.feature_importances_)
    }


def drop_low_variance(df: pd.DataFrame, threshold: float = 0.01) -> pd.DataFrame:
    """Elimina columnas numéricas con varianza menor al umbral."""
    numeric = df.select_dtypes(include="number")
    low_var = numeric.columns[numeric.var() < threshold].tolist()
    if low_var:
        logger.info("Columnas de baja varianza eliminadas: %s", low_var)
    return df.drop(columns=low_var, errors="ignore")


def select_top_features(
    df: pd.DataFrame,
    importances: dict[str, float],
    top_n: int = 6,
) -> list[str]:
    """Retorna los top N features según importancia."""
    ranked = sorted(importances.items(), key=lambda x: x[1], reverse=True)
    selected = [name for name, _ in ranked[:top_n] if name in df.columns]
    logger.info("Features seleccionadas: %s", selected)
    return selected
