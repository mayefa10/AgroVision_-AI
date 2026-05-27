"""Servicio ETL para construcción del dataset maestro."""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from config.constants import DEPARTAMENTOS_ETL, ENSO_HISTORICO, PathConfig
from domain.models import ETLResult
from infrastructure.clients.eva_client import EVAClient
from infrastructure.clients.nasa_client import NASAClient

logger = logging.getLogger(__name__)


class ETLService:
    """Pipeline ETL: EVA + NASA POWER + ENSO."""
    
    def __init__(self):
        PathConfig.ensure_dirs()
        self.eva_client = EVAClient()
        self.nasa_client = NASAClient()
    
    async def build_dataset(self, max_eva: int = 30000) -> ETLResult:
        """Ejecuta pipeline ETL completo."""
        inicio = datetime.now(timezone.utc)
        logger.info("=== INICIANDO ETL PIPELINE ===")
        
        # 1. Fetch EVA
        eva_raw = await self._fetch_eva(max_eva)
        eva_raw.to_csv(f"{PathConfig.RAW}/eva_raw.csv", index=False)
        
        # 2. Limpiar EVA
        eva_clean = self._clean_eva(eva_raw)
        eva_clean.to_csv(f"{PathConfig.PROCESSED}/eva_clean.csv", index=False)
        
        # 3. Clima histórico
        anios = self._extract_years(eva_clean)
        clima = await self._fetch_climate(anios)
        clima.to_csv(f"{PathConfig.PROCESSED}/clima_historico.csv", index=False)
        
        # 4. Merge EVA + Clima
        merged = self._merge_climate(eva_clean, clima)
        
        # 5. ENSO
        merged = self._add_enso(merged)
        
        # 6. Feature engineering
        dataset_final = self._feature_engineering(merged)
        dataset_final.to_csv(f"{PathConfig.FEATURES}/dataset_maestro.csv", index=False)
        
        # Stats
        duracion = (datetime.now(timezone.utc) - inicio).seconds
        
        result = ETLResult(
            success=True,
            duracion_segundos=duracion,
            registros_eva_raw=len(eva_raw),
            registros_eva_clean=len(eva_clean),
            registros_dataset_final=len(dataset_final),
            departamentos=dataset_final["departamento"].nunique(),
            cultivos=dataset_final["cultivo"].nunique(),
            anios=sorted(dataset_final["anio"].unique().tolist()),
            columnas=list(dataset_final.columns),
            archivos={
                "raw": f"{PathConfig.RAW}/eva_raw.csv",
                "clean": f"{PathConfig.PROCESSED}/eva_clean.csv",
                "clima": f"{PathConfig.PROCESSED}/clima_historico.csv",
                "maestro": f"{PathConfig.FEATURES}/dataset_maestro.csv",
            },
        )
        
        logger.info(f"=== ETL COMPLETADO en {duracion}s ===")
        return result
    
    async def _fetch_eva(self, max_records: int) -> pd.DataFrame:
        """Descarga datos EVA completos."""
        logger.info("Descargando EVA...")
        df = await self.eva_client.fetch_training_data(limit=max_records)
        logger.info(f"EVA total: {len(df)} registros")
        return df
    
    def _clean_eva(self, df: pd.DataFrame) -> pd.DataFrame:
        """Limpieza y normalización."""
        if df.empty:
            return df
        
        # Parsear periodo
        def parse_periodo(p):
            if pd.isna(p):
                return 0
            p = str(p).upper()
            if "PRIMER" in p or "1" in p:
                return 1
            if "SEGUNDO" in p or "2" in p:
                return 2
            return 0
        
        if "periodo" in df.columns:
            df["semestre"] = df["periodo"].apply(parse_periodo)
        
        # Filtros de calidad
        df = df.dropna(subset=["departamento", "cultivo", "anio", "rendimiento"])
        df = df[df["rendimiento"] > 0]
        df = df[df["rendimiento"] < 200]
        df = df[df["area_sembrada"] > 0]
        df = df[df["anio"] >= 2007]
        
        # Eliminar duplicados
        df = df.drop_duplicates(
            subset=["departamento", "municipio", "cultivo", "anio", "semestre"],
            keep="last",
        )
        
        logger.info(f"EVA limpio: {len(df)} registros")
        return df.reset_index(drop=True)
    
    def _extract_years(self, df: pd.DataFrame) -> List[int]:
        """Extrae años válidos del dataset."""
        anios = df["anio"].dropna().unique().tolist()
        return [int(a) for a in anios if 2007 <= int(a) <= 2024]
    
    async def _fetch_climate(self, anios: List[int]) -> pd.DataFrame:
        """Descarga clima histórico para todos los departamentos."""
        # Limitar para demo
        anios = anios[:5]
        
        tasks = []
        for dept, info in DEPARTAMENTOS_ETL.items():
            for anio in anios:
                tasks.append(self.nasa_client.fetch_annual(
                    lat=info.lat,
                    lng=info.lng,
                    anio=anio,
                    departamento=dept,
                ))
        
        logger.info(f"Descargando clima para {len(tasks)} combinaciones...")
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        rows = [
            r for r in results
            if isinstance(r, dict) and r.get("temp_promedio") is not None
        ]
        
        if not rows:
            logger.warning("NASA POWER devolvió 0 registros válidos")
            return pd.DataFrame(columns=[
                "departamento", "anio", "temp_promedio",
                "precipitacion", "humedad", "radiacion_solar",
            ])
        
        return pd.DataFrame(rows)
    
    def _merge_climate(
        self,
        eva: pd.DataFrame,
        clima: pd.DataFrame,
    ) -> pd.DataFrame:
        """Merge EVA con datos climáticos."""
        eva["anio"] = eva["anio"].astype(int)
        
        if clima.empty:
            logger.warning("Dataset clima vacío — continuando sin variables climáticas")
            return eva
        
        clima["anio"] = clima["anio"].astype(int)
        return eva.merge(clima, on=["departamento", "anio"], how="left")
    
    def _add_enso(self, df: pd.DataFrame) -> pd.DataFrame:
        """Agrega variables ENSO."""
        enso_data = [
            {
                "anio": anio,
                "enso_fase": entry.fase,
                "enso_intensidad": entry.intensidad,
                "oni_index": entry.oni,
                "es_el_nino": int(entry.es_el_nino),
                "es_la_nina": int(entry.es_la_nina),
            }
            for anio, entry in ENSO_HISTORICO.items()
        ]
        
        enso_df = pd.DataFrame(enso_data)
        df["anio"] = df["anio"].astype(int)
        
        return df.merge(enso_df, on="anio", how="left")
    
    def _feature_engineering(self, df: pd.DataFrame) -> pd.DataFrame:
        """Crea variables derivadas."""
        # Rendimiento histórico promedio
        rend_hist = (
            df.groupby(["departamento", "cultivo"])["rendimiento"]
            .mean()
            .reset_index()
        )
        rend_hist.columns = ["departamento", "cultivo", "rendimiento_hist_promedio"]
        df = df.merge(rend_hist, on=["departamento", "cultivo"], how="left")
        
        # Desviación respecto a histórico
        df["rendimiento_vs_historico"] = df["rendimiento"] - df["rendimiento_hist_promedio"]
        
        # Ratio cosecha
        if "area_cosechada" in df.columns and "area_sembrada" in df.columns:
            df["ratio_cosecha"] = (df["area_cosechada"] / df["area_sembrada"]).clip(0, 1)
        
        # Impacto ENSO
        if "es_el_nino" in df.columns:
            rend_nino = (
                df[df["es_el_nino"] == 1]
                .groupby(["departamento", "cultivo"])["rendimiento"]
                .mean()
            )
            rend_normal = (
                df[df["es_el_nino"] == 0]
                .groupby(["departamento", "cultivo"])["rendimiento"]
                .mean()
            )
            impacto = (rend_nino - rend_normal).reset_index()
            impacto.columns = ["departamento", "cultivo", "impacto_el_nino"]
            df = df.merge(impacto, on=["departamento", "cultivo"], how="left")
        
        # Categorías de riesgo
        if "oni_index" in df.columns:
            df["riesgo_climatico"] = pd.cut(
                df["oni_index"],
                bins=[-float("inf"), -1.5, -0.5, 0.5, 1.5, float("inf")],
                labels=["la_nina_fuerte", "la_nina", "neutro", "el_nino", "el_nino_fuerte"],
            )
        
        return df