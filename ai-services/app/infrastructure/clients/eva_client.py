"""AgroVision AI — Cliente EVA (datos.gov.co)."""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

import pandas as pd

from app.config.constants import EVA_2019_2024, SOCRATA_BASE
from .base_client import BaseHttpClient

logger = logging.getLogger(__name__)

# ── Mapa canónico de renombrado ───────────────────────────
# La API Socrata devuelve nombres con caracteres especiales
# que varían según la versión del dataset.
_EVA_RENAME: dict[str, str] = {
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
    # Nombres alternativos posibles
    "year":         "anio",
    "area_planted": "area_sembrada",
    "area_harvest": "area_cosechada",
    "production":   "produccion",
    "yield":        "rendimiento",
}

# Columnas que deben ser numéricas tras el renombrado
_NUMERIC_COLS = ["area_sembrada", "area_cosechada", "produccion", "rendimiento", "anio"]

# Columnas que NO deben rellenarse con 0 cuando son nulas —
# son métricas reales y un 0 es engañoso para el usuario/modelo.
_NO_FILLNA_ZERO = {"area_sembrada", "area_cosechada", "produccion"}


def _normalizar_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Renombra columnas al esquema canónico y convierte tipos numéricos.
    Llamado en fetch(), fetch_paginated() y fetch_summary() para
    garantizar columnas consistentes en toda la app.
    """
    rename_aplicar = {k: v for k, v in _EVA_RENAME.items() if k in df.columns}
    if rename_aplicar:
        df = df.rename(columns=rename_aplicar)
        logger.debug("EVA rename aplicado: %s", list(rename_aplicar.keys()))

    for col in _NUMERIC_COLS:
        if col in df.columns:
            # errors='coerce' → strings vacíos / "N/A" se convierten en NaN (no 0)
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def _safe_fillna(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rellena nulos de forma selectiva antes de serializar a dict:
      - Columnas métricas (area, produccion) → None  (el frontend muestra "—")
      - Resto de columnas object → "" para evitar 'null' en JSON
      - Numéricos no métricos → 0

    Así evitamos que áreas reales de 0 ha engañen al usuario.
    """
    df = df.copy()
    for col in df.columns:
        if col in _NO_FILLNA_ZERO:
            # Mantener NaN → se serializa como None/null en JSON
            continue
        elif df[col].dtype == object:
            df[col] = df[col].fillna("")
        else:
            df[col] = df[col].fillna(0)
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
            # La API usa 'a_o' en el $where aunque renombremos localmente
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

        # Filtro base: solo registros con rendimiento válido
        # NO filtramos area_sembrada aquí — hay registros legítimos sin área
        # registrada en la fuente (especialmente años recientes).
        where_clauses = ["rendimiento IS NOT NULL", "rendimiento > 0"]
        extra = self._build_where(departamento, cultivo, anio)
        if extra:
            where_clauses.append(extra)
        params["$where"] = " AND ".join(where_clauses)

        data = await self.get_safe(f"/{dataset}.json", params=params, default=[])
        if not data:
            return {"success": False, "message": "Sin datos EVA", "data": []}

        df = pd.DataFrame(data)
        if df.empty:
            return {"success": False, "message": "Sin datos EVA", "data": []}

        # ── Renombrado + conversión de tipos ──────────────
        df = _normalizar_df(df)

        # ── Estadísticas (ignoran NaN automáticamente) ────
        stats: dict = {}
        if "rendimiento" in df.columns:
            stats["rendimiento_promedio"] = round(df["rendimiento"].mean(skipna=True), 2)
            stats["rendimiento_max"]      = round(df["rendimiento"].max(skipna=True), 2)
            stats["rendimiento_min"]      = round(df["rendimiento"].min(skipna=True), 2)
        if "produccion" in df.columns:
            stats["produccion_total"]    = round(df["produccion"].sum(skipna=True), 2)
        if "area_sembrada" in df.columns:
            stats["area_sembrada_total"] = round(df["area_sembrada"].sum(skipna=True), 2)
        stats["registros_sin_area"] = int(
            df["area_sembrada"].isna().sum() if "area_sembrada" in df.columns else 0
        )

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
            # _safe_fillna: métricas nulas quedan null (no 0) en el JSON
            "data":            _safe_fillna(df).to_dict(orient="records"),
            "fetched_at":      datetime.now(timezone.utc).isoformat(),
        }

    async def fetch_paginated(
        self,
        limit: int = 5000,
        dataset: str = EVA_2019_2024,
        extra_where: str = "rendimiento IS NOT NULL AND rendimiento > 0",
    ) -> pd.DataFrame:
        """
        Descarga masiva paginando de a 1000 registros.
        Retorna DataFrame con columnas canónicas y tipos correctos.

        Cambio respecto a la versión anterior:
          - Ya NO filtra 'rea_sembrada IS NOT NULL' para no perder
            registros válidos con área sin reportar en la fuente.
          - Sí filtra rendimiento > 0 para excluir filas sin valor útil.
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

        return _normalizar_df(pd.DataFrame(all_data))

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
            "$where": "rendimiento IS NOT NULL AND rendimiento > 0",
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
            "data":       _safe_fillna(df).to_dict(orient="records"),
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }


# Instancia singleton
eva_client = EvaClient()