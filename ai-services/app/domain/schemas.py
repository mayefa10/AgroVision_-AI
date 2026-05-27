"""Esquemas Pydantic para request/response de la API."""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PredictionType(str, Enum):
    SEQUIA = "sequia"
    INUNDACION = "inundacion"
    HELADA = "helada"
    RENDIMIENTO = "rendimiento_cultivo"


class ENSOPhase(str, Enum):
    EL_NINO = "El Nino"
    LA_NINA = "La Nina"
    NEUTRO = "Neutro"


class GeoCoords(BaseModel):
    lat: float
    lng: float


class ClimateStats(BaseModel):
    temperatura_promedio: Optional[float] = None
    temperatura_max: Optional[float] = None
    temperatura_min: Optional[float] = None
    precipitacion_total: Optional[float] = None
    humedad_promedio: Optional[float] = None
    dias_sin_lluvia: Optional[int] = None
    dias_con_lluvia: Optional[int] = None


class ClimateRecord(BaseModel):
    fecha: str
    temperatura: float
    precipitacion: float
    humedad: float
    radiacion_solar: float
    viento: float


class ClimateData(BaseModel):
    success: bool = True
    source: str = "NASA POWER"
    departamento: Optional[str] = None
    coordenadas: GeoCoords
    periodo: Dict[str, Any] = {}
    estadisticas: ClimateStats = ClimateStats()
    data: List[ClimateRecord] = []
    fetched_at: Optional[datetime] = None


class EVASummary(BaseModel):
    success: bool
    source: str = "EVA — datos.gov.co"
    dataset_id: str
    total_registros: int
    filtros: Dict[str, Any]
    estadisticas: Dict[str, float]
    data: List[Dict[str, Any]]
    fetched_at: datetime


class RiskPredictionRequest(BaseModel):
    region_code: str = Field(..., example="05001")
    prediction_type: PredictionType = PredictionType.SEQUIA
    temperatura: float = Field(..., ge=-10, le=50, example=28.5)
    humedad: float = Field(..., ge=0, le=100, example=65.0)
    precipitacion: float = Field(..., ge=0, example=12.0)
    viento: Optional[float] = Field(None, example=8.5)
    altitud: Optional[float] = Field(None, example=1500.0)


class RiskPredictionResponse(BaseModel):
    region_code: str
    prediction_type: str
    risk: RiskLevel
    confidence: float
    message: str
    variables_used: Dict[str, Optional[float]]


class RendimientoRequest(BaseModel):
    departamento: str = "ANTIOQUIA"
    cultivo: str = "MAIZ"
    grupo_cultivo: str = "CEREALES Y LEGUMINOSAS"
    area_sembrada: float = 100.0
    anio: int = 2024
    periodo: int = 1


class RendimientoResponse(BaseModel):
    success: bool
    departamento: str
    cultivo: str
    rendimiento_predicho: float
    unidad: str = "t/ha"
    nivel: str
    anio: int
    area_sembrada: float


class MLTrainingResult(BaseModel):
    success: bool
    registros_entrenamiento: int
    registros_test: int
    mae: float
    r2: float
    feature_importance: Dict[str, float]
    model_path: str


class ETLResult(BaseModel):
    success: bool
    duracion_segundos: int
    registros_eva_raw: int
    registros_eva_clean: int
    registros_dataset_final: int
    departamentos: int
    cultivos: int
    anios: List[int]
    columnas: List[str]
    archivos: Dict[str, str]


class Alerta(BaseModel):
    id: str
    tipo: str
    severidad: str
    departamento: str
    titulo: str
    mensaje: str
    cultivos_afectados: List[str]
    variables: Dict[str, float]
    recomendacion: str
    score: int
    fecha: str
    activa: bool = True


class AlertasResponse(BaseModel):
    success: bool
    departamento: str
    clima_actual: Dict[str, Any]
    total_alertas: int
    alertas: List[Alerta]
    fecha_generacion: str


class HealthStatus(BaseModel):
    service: str
    version: str
    status: str
