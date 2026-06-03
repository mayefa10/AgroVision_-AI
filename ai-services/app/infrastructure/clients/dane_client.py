"""AgroVision AI — Cliente DANE / DIVIPOLA."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

import pandas as pd

from app.config.constants import DIVIPOLA_CODIGOS, DIVIPOLA_GEO, SOCRATA_BASE
from .base_client import BaseHttpClient

logger = logging.getLogger(__name__)

# Mapeo canónico de nombres de columna → nombre estándar
_COL_MAP: dict[str, str] = {
    "cod_mpio":             "codigo_municipio",
    "codigo_municipio":     "codigo_municipio",
    "cod_municipio":        "codigo_municipio",
    "nom_mpio":             "nombre_municipio",
    "nombre_municipio":     "nombre_municipio",
    "municipio":            "nombre_municipio",
    "nom_dep":              "nombre_departamento",
    "nombre_departamento":  "nombre_departamento",
    "departamento":         "nombre_departamento",
    "cod_dep":              "codigo_departamento",
    "codigo_departamento":  "codigo_departamento",
    "latitud":              "latitud",
    "lat":                  "latitud",
    "longitud":             "longitud",
    "lng":                  "longitud",
    "lon":                  "longitud",
}


def _normalizar_columnas(df: pd.DataFrame) -> pd.DataFrame:
    col_map = {c: _COL_MAP[c.lower()] for c in df.columns if c.lower() in _COL_MAP}
    return df.rename(columns=col_map)


def _extraer_point(x: object) -> tuple[float, float]:
    """Extrae lat/lng de un campo 'point' dict, case-insensitive."""
    if not isinstance(x, dict):
        return 0.0, 0.0
    lower = {k.lower(): v for k, v in x.items()}
    return float(lower.get("latitude", 0)), float(lower.get("longitude", 0))


class DaneClient(BaseHttpClient):

    def __init__(self) -> None:
        super().__init__(base_url=SOCRATA_BASE, timeout=30.0)

    async def fetch_geo(
        self,
        departamento: Optional[str] = None,
        limit: int = 1200,
    ) -> dict:
        params: dict = {"$limit": limit}
        if departamento:
            params["$where"] = f"upper(nom_dep)='{departamento.upper()}'"

        data = await self.get_safe(f"/{DIVIPOLA_GEO}.json", params=params, default=[])
        if not data:
            return {"success": False, "message": "Sin datos DIVIPOLA geo", "data": []}

        df = _normalizar_columnas(pd.DataFrame(data))

        if "latitud" not in df.columns and "point" in df.columns:
            coords = df["point"].apply(_extraer_point)
            df["latitud"]  = coords.apply(lambda t: t[0])
            df["longitud"] = coords.apply(lambda t: t[1])

        for col in ["latitud", "longitud"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        return {
            "success":            True,
            "source":             "DANE — DIVIPOLA Geolocalizados",
            "total_municipios":   len(df),
            "departamento_filtro": departamento,
            "data":               df.fillna("").to_dict(orient="records"),
            "fetched_at":         datetime.utcnow().isoformat(),
        }

    async def fetch_codigos(
        self,
        departamento: Optional[str] = None,
        codigo_municipio: Optional[str] = None,
        limit: int = 1200,
    ) -> dict:
        params: dict = {"$limit": limit}
        where: list[str] = []
        if departamento:
            where.append(f"upper(nombre_departamento)='{departamento.upper()}'")
        if codigo_municipio:
            where.append(f"codigo_municipio='{codigo_municipio}'")
        if where:
            params["$where"] = " AND ".join(where)

        data = await self.get_safe(f"/{DIVIPOLA_CODIGOS}.json", params=params, default=[])
        return {
            "success":    bool(data),
            "source":     "DANE — DIVIPOLA Códigos",
            "total":      len(data) if data else 0,
            "data":       data or [],
            "fetched_at": datetime.utcnow().isoformat(),
        }

    async def lookup(self, nombre: str, limit: int = 10) -> dict:
        """Búsqueda por nombre de municipio con sanitización contra SoQL injection."""
        nombre_safe = nombre.replace("'", "''").strip()
        params = {
            "$where": f"upper(nombre_municipio) like '%{nombre_safe.upper()}%'",
            "$limit": limit,
        }
        data = await self.get_safe(f"/{DIVIPOLA_CODIGOS}.json", params=params, default=[])
        return {
            "success":    True,
            "query":      nombre,
            "resultados": len(data) if data else 0,
            "data":       data or [],
        }
