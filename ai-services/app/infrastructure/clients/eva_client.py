"""AgroVision AI — Cliente EVA (datos.gov.co)."""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

import pandas as pd

from app.config.constants import EVA_2019_2024, SOCRATA_BASE
from .base_client import BaseHttpClient

logger = logging.getLogger(__name__)

# ── Mapa canónico de renombrado de columnas EVA ───────────
# La API Socrata devuelve nombres con caracteres especiales
# que varían según la versión del dataset.
_EVA_RENAME: dict[str, str] = {
    # Nombres con caracteres especiales (versión Socrata)
    "a_o":                           "anio",
    "rea_sembrada":                  "area_sembrada",
    "rea_cosechada":                 "area_cosechada",
    "producci_n":                    "produccion",
    "desagregaci_n_cultivo":         "desagregacion_cultivo",
    "ciclo_del_cultivo":             "ciclo_cultivo",
    "estado_f_sico_del_cultivo":     "estado_fisico",
    "c_digo_del_cultivo":            "codigo_cultivo",
    "c_digo_dane_departamento":      "codigo_dane_dpto",
    "c_digo_dane_municipio":         "codigo_dane_mpio",
    "nombre_cient_fico_del_cultivo": "nombre_cientifico",
    # Nombres alternativos que puede traer la API
    "year":          "anio",
    "area_planted":  "area_sembrada",
    "area_harvest":  "area_cosechada",
    "production":    "produccion",
    "yield":         "rendimiento",
}

# Columnas numéricas finales (después del renombrado)
_NUMERIC_COLS = ["area_sembrada", "area_cosechada", "produccion", "rendimiento", "anio"]


def _normalizar_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica el renombrado canónico y convierte tipos numéricos.
    Se llama en fetch(), fetch_paginated() y fetch_summary()
    para garantizar columnas consistentes en toda la app.
    """
    # Renombrar solo las columnas presentes
    rename_aplicar = {k: v for k, v in _EVA_RENAME.items() if k in df.columns}
    if rename_aplicar:
        df = df.rename(columns=rename_aplicar)
        logger.debug("EVA rename aplicado: %s", list(rename_aplicar.keys()))

    # Convertir numéricos
    for col in _NUMERIC_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


class EvaClient(BaseHttpClient):

    def __init__(self) -> None:
        super().__init__(base_url=SOCRATA_BASE, timeout=60.0)

    def _build_where(
        self,
        departamento: Optional[str],
        cultivo: Optional[str],
        anio: Optional[int],
        extra: Optional[str] = None,
    ) -> Optional[str]:
        clauses: list[str] = []
        if departamento:
            clauses.append(f"upper(departamento)='{departamento.upper()}'")
        if cultivo:
            clauses.append(f"upper(cultivo)='{cultivo.upper()}'")
        if anio:
            # La API usa 'a_o' en el $where aunque ya renombremos localmente
            clauses.append(f"a_o={anio}")
        if extra:
            clauses.append(extra)
        return " AND ".join(clauses) if clauses else None

    async def fetch(
        self,
        departamento: Optional[str] = None,
        cultivo: Optional[str] = None,
        anio: Optional[int] = None,
        limit: int = 1000,
        dataset: str = EVA_2019_2024,
    ) -> dict:
        params: dict = {"$limit": limit, "$order": "a_o DESC"}
        where = self._build_where(departamento, cultivo, anio)
        if where:
            params["$where"] = where

        data = await self.get_safe(f"/{dataset}.json", params=params, default=[])
        if not data:
            return {"success": False, "message": "Sin datos EVA", "data": []}

        df = pd.DataFrame(data)
        if df.empty:
            return {"success": False, "message": "Sin datos EVA", "data": []}

        # ── Renombrado + conversión de tipos ──────────────
        df = _normalizar_df(df)

        # ── Estadísticas ──────────────────────────────────
        stats: dict = {}
        if "rendimiento" in df.columns:
            stats["rendimiento_promedio"] = round(df["rendimiento"].mean(skipna=True), 2)
            stats["rendimiento_max"]      = round(df["rendimiento"].max(skipna=True), 2)
            stats["rendimiento_min"]      = round(df["rendimiento"].min(skipna=True), 2)
        if "produccion" in df.columns:
            stats["produccion_total"]     = round(df["produccion"].sum(skipna=True), 2)
        if "area_sembrada" in df.columns:
            stats["area_sembrada_total"]  = round(df["area_sembrada"].sum(skipna=True), 2)

        return {
            "success":         True,
            "source":          "EVA — datos.gov.co",
            "dataset_id":      dataset,
            "total_registros": len(df),
            "filtros":         {
                "departamento": departamento,
                "cultivo":      cultivo,
                "anio":         anio,
            },
            "estadisticas":    stats,
            "data":            df.fillna(0).to_dict(orient="records"),
            "fetched_at":      datetime.now(timezone.utc).isoformat(),
        }

    async def fetch_paginated(
        self,
        limit: int = 5000,
        dataset: str = EVA_2019_2024,
        extra_where: str = "rendimiento IS NOT NULL AND rea_sembrada IS NOT NULL",
    ) -> pd.DataFrame:
        """
        Descarga masiva paginando de a 1000 registros.
        Retorna un DataFrame ya con columnas normalizadas y tipos correctos,
        listo para pasar directo al ETL / cleaner sin transformaciones adicionales.
        """
        all_data: list[dict] = []

        for offset in range(0, limit, 1000):
            params = {
                "$limit":  1000,
                "$offset": offset,
                "$order":  "a_o DESC",
                "$where":  extra_where,
            }
            batch = await self.get_safe(f"/{dataset}.json", params=params, default=[])
            if not batch:
                break
            all_data.extend(batch)
            logger.debug("EVA: %d registros acumulados", len(all_data))

        logger.info("EVA descarga completa: %d registros", len(all_data))

        if not all_data:
            return pd.DataFrame()

        # ── Renombrado + conversión de tipos ──────────────
        df = _normalizar_df(pd.DataFrame(all_data))
        return df

    async def fetch_summary(self, dataset: str = EVA_2019_2024) -> dict:
        """Resumen nacional: top cultivos y departamentos por producción."""
        params = {
            "$select": (
                "departamento, cultivo, "
                "sum(produccion) as produccion_total, "
                "sum(rea_sembrada) as area_total, "
                "avg(rendimiento) as rendimiento_promedio, "
                "max(a_o) as ultimo_anio"
            ),
            "$group": "departamento, cultivo",
            "$order": "produccion_total DESC",
            "$limit": 50,
        }
        data = await self.get_safe(f"/{dataset}.json", params=params, default=[])
        if not data:
            return {"success": False, "message": "Sin datos", "data": []}

        df = pd.DataFrame(data)

        # Renombrar columnas de la proyección SoQL
        df = df.rename(columns={
            "produccion_total":      "produccion_total",   # ya viene bien
            "area_total":            "area_total",
            "rendimiento_promedio":  "rendimiento_promedio",
            "ultimo_anio":           "ultimo_anio",
        })

        for col in ["produccion_total", "area_total", "rendimiento_promedio"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").round(2)

        return {
            "success":    True,
            "source":     "EVA — datos.gov.co",
            "data":       df.fillna(0).to_dict(orient="records"),
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }


# Instancia singleton — importar desde aquí en los servicios
eva_client = EvaClient()