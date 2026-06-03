"""AgroVision AI — Schemas Pydantic (request / response)."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from .enums import AlertSeverity, AlertType, PredictionType, RiskLevel, YieldLevel


# ── Predicción de riesgo ──────────────────────────────────

class PredictRiskRequest(BaseModel):
    region_code:     str            = Field(..., example="05001")
    prediction_type: PredictionType = PredictionType.SEQUIA
    temperatura:     float          = Field(..., ge=-10, le=50,  example=28.5)
    humedad:         float          = Field(..., ge=0,   le=100, example=65.0)
    precipitacion:   float          = Field(..., ge=0,           example=12.0)
    viento:          Optional[float] = Field(None, example=8.5)
    altitud:         Optional[float] = Field(None, example=1500.0)


class PredictRiskResponse(BaseModel):
    region_code:     str
    prediction_type: str
    risk:            RiskLevel
    confidence:      float
    message:         str
    variables_used:  dict[str, Any]


# ── Predicción de rendimiento ─────────────────────────────

class RendimientoRequest(BaseModel):
    departamento:  str   = "ANTIOQUIA"
    cultivo:       str   = "MAIZ"
    grupo_cultivo: str   = "CEREALES Y LEGUMINOSAS"
    area_sembrada: float = 100.0
    anio:          int   = 2024
    periodo:       int   = 1


class RendimientoResponse(BaseModel):
    success:              bool
    departamento:         str
    cultivo:              str
    rendimiento_predicho: float
    unidad:               str
    nivel:                YieldLevel
    anio:                 int
    area_sembrada:        float


# ── Alertas ───────────────────────────────────────────────

class AlertaResponse(BaseModel):
    id:                 str
    tipo:               AlertType
    severidad:          AlertSeverity
    departamento:       str
    titulo:             str
    mensaje:            str
    cultivos_afectados: list[str]
    variables:          dict[str, float]
    recomendacion:      str
    score:              int
    fecha:              str
    activa:             bool


class AlertasDepartamentoResponse(BaseModel):
    success:          bool
    departamento:     str
    clima_actual:     dict[str, Any]
    total_alertas:    int
    alertas:          list[AlertaResponse]
    fecha_generacion: str


# ── Clima ─────────────────────────────────────────────────

class ClimaPeriodo(BaseModel):
    inicio: str
    fin:    str
    dias:   int


class NasaStatsResponse(BaseModel):
    temperatura_promedio:   float
    temperatura_max:        float
    temperatura_min:        float
    precipitacion_promedio: float
    precipitacion_total:    float
    humedad_promedio:       float
    dias_sin_lluvia:        int
    dias_con_lluvia:        int
