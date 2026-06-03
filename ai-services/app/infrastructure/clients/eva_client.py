"""AgroVision AI — Cliente EVA (datos.gov.co)."""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

import pandas as pd

from app.config.constants import EVA_2019_2024, SOCRATA_BASE
from .base_client import BaseHttpClient

logger = logging.getLogger(__name__)


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

        numeric_cols = ["area_sembrada", "area_cosechada", "produccion", "rendimiento"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

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
            "filtros":         {"departamento": departamento, "cultivo": cultivo, "anio": anio},
            "estadisticas":    stats,
            "data":            df.fillna(0).to_dict(orient="records"),
            "fetched_at":      datetime.utcnow().isoformat(),
        }

    async def fetch_paginated(
        self,
        limit: int = 5000,
        dataset: str = EVA_2019_2024,
        extra_where: str = "rendimiento IS NOT NULL AND rea_sembrada IS NOT NULL",
    ) -> pd.DataFrame:
        """Descarga masiva paginando de a 1000 registros."""
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
        return pd.DataFrame(all_data)

    async def fetch_summary(self, dataset: str = EVA_2019_2024) -> dict:
        params = {
            "$select": (
                "departamento, cultivo, "
                "sum(produccion) as produccion_total, "
                "sum(area_sembrada) as area_total, "
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
        for col in ["produccion_total", "area_total", "rendimiento_promedio"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").round(2)

        return {
            "success":    True,
            "source":     "EVA — datos.gov.co",
            "data":       df.fillna(0).to_dict(orient="records"),
            "fetched_at": datetime.now(timezone.utc).isoformat()
        }
# Instancia singleton
eva_client = EvaClient()