"""AgroVision AI — Servicio ETL."""
# Copyright (C) 2026 July Mayerly Quintero Farfán

from __future__ import annotations

from datetime import datetime

from app.config.constants import ENSO_HISTORICO
from app.etl.pipelines.master_pipeline import run_master_pipeline


async def build_dataset(max_eva: int = 30000) -> dict:
    return await run_master_pipeline(max_eva)


def get_enso_historico() -> dict:
    return {
        "fuente": "NOAA ONI Index",
        "data": [
            {
                "anio":              anio,
                "fase":              v["fase"],
                "intensidad":        v["intensidad"],
                "oni_index":         v["oni"],
                "impacto_colombia":  (
                    "Sequías" if v["fase"] == "El Nino"
                    else "Lluvias excesivas" if v["fase"] == "La Nina"
                    else "Normal"
                ),
            }
            for anio, v in ENSO_HISTORICO.items()
        ],
    }


def get_enso_actual() -> dict:
    anio = datetime.utcnow().year
    enso = ENSO_HISTORICO.get(anio) or ENSO_HISTORICO.get(max(ENSO_HISTORICO))
    return {
        "anio":       anio,
        "fase":       enso["fase"],
        "intensidad": enso["intensidad"],
        "oni_index":  enso["oni"],
        "alerta":     enso["fase"] != "Neutro",
        "mensaje": (
            f"Fase {enso['fase']} activa. ONI={enso['oni']}. "
            + ("Riesgo de sequías." if enso["fase"] == "El Nino"
               else "Riesgo de lluvias excesivas." if enso["fase"] == "La Nina"
               else "Condiciones normales.")
        ),
    }
