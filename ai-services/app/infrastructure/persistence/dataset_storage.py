"""AgroVision AI — Persistencia de datasets en disco."""
from __future__ import annotations

import logging
import os

import pandas as pd

from app.config.constants import FEATURES_PATH, PROCESSED_PATH, RAW_PATH

logger = logging.getLogger(__name__)


def _ensure_dirs() -> None:
    for path in [RAW_PATH, PROCESSED_PATH, FEATURES_PATH]:
        os.makedirs(path, exist_ok=True)


class DatasetStorage:
    """Guarda y carga DataFrames como CSV."""

    @staticmethod
    def save_raw(df: pd.DataFrame, name: str) -> str:
        _ensure_dirs()
        path = f"{RAW_PATH}/{name}.csv"
        df.to_csv(path, index=False)
        logger.info("Guardado raw: %s (%d filas)", path, len(df))
        return path

    @staticmethod
    def save_processed(df: pd.DataFrame, name: str) -> str:
        _ensure_dirs()
        path = f"{PROCESSED_PATH}/{name}.csv"
        df.to_csv(path, index=False)
        logger.info("Guardado processed: %s (%d filas)", path, len(df))
        return path

    @staticmethod
    def save_features(df: pd.DataFrame, name: str) -> str:
        _ensure_dirs()
        path = f"{FEATURES_PATH}/{name}.csv"
        df.to_csv(path, index=False)
        logger.info("Guardado features: %s (%d filas)", path, len(df))
        return path

    @staticmethod
    def load(path: str) -> pd.DataFrame:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Dataset no encontrado: {path}")
        return pd.read_csv(path)
