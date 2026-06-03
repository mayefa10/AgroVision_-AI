"""AgroVision AI — Modelo Random Forest de rendimiento agrícola."""
from __future__ import annotations

import pandas as pd
from sklearn.ensemble import RandomForestRegressor

from .base import BaseModel


class AgroRandomForest(BaseModel):
    """
    Random Forest entrenado con datos EVA para predecir rendimiento (t/ha).
    Parámetros calibrados para datos agrícolas colombianos.
    """

    name = "random_forest"

    def __init__(
        self,
        n_estimators: int = 200,
        max_depth: int = 12,
        min_samples_split: int = 5,
        min_samples_leaf: int = 2,
        random_state: int = 42,
    ) -> None:
        self._model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            random_state=random_state,
            n_jobs=-1,
        )

    def fit(self, X: pd.DataFrame, y: pd.Series) -> "AgroRandomForest":
        self._model.fit(X, y)
        return self

    def predict(self, X: pd.DataFrame) -> list[float]:
        return self._model.predict(X).tolist()

    @property
    def feature_importances_(self):
        return self._model.feature_importances_

    def get_params(self) -> dict:
        return self._model.get_params()

    @property
    def sklearn_model(self):
        """Acceso directo al estimador sklearn (para compatibilidad)."""
        return self._model
