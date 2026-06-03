"""AgroVision AI — Transformador ENSO."""
from __future__ import annotations

import pandas as pd

from app.config.constants import ENSO_HISTORICO


def add_enso(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega columnas ENSO al DataFrame (merge por año)."""
    enso_rows = [
        {
            "anio":           anio,
            "enso_fase":      v["fase"],
            "enso_intensidad":v["intensidad"],
            "oni_index":      v["oni"],
            "es_el_nino":     int(v["fase"] == "El Nino"),
            "es_la_nina":     int(v["fase"] == "La Nina"),
        }
        for anio, v in ENSO_HISTORICO.items()
    ]
    enso_df = pd.DataFrame(enso_rows)
    enso_df["anio"] = enso_df["anio"].astype(int)

    df = df.copy()
    df["anio"] = df["anio"].astype(int)
    return df.merge(enso_df, on="anio", how="left")
