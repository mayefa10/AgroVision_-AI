"""AgroVision AI — Clase base para modelos ML."""
# Copyright (C) 2026 July Mayerly Quintero Farfán

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import pandas as pd


class BaseModel(ABC):
    """Interfaz común para todos los modelos de AgroVision."""

    name: str = "base"

    @abstractmethod
    def fit(self, X: pd.DataFrame, y: pd.Series) -> "BaseModel":
        ...

    @abstractmethod
    def predict(self, X: pd.DataFrame) -> Any:
        ...

    @abstractmethod
    def get_params(self) -> dict:
        ...
