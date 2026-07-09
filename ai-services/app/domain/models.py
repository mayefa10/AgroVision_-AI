"""
AgroVision AI — Modelos de dominio.
Representaciones internas de los datos (no Pydantic, no ORM).
Usadas por los servicios para pasar datos entre capas.
"""
# Copyright (C) 2026 July Mayerly Quintero Farfán

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DepartamentoInfo:
    nombre:  str
    lat:     float
    lng:     float
    capital: str
    codigo:  str
    cultivos: list[str] = field(default_factory=list)


@dataclass
class ClimaPeriodo:
    temperatura_promedio:   float
    temperatura_max:        float
    temperatura_min:        float
    precipitacion_promedio: float
    precipitacion_total:    float
    humedad_promedio:       float
    dias_sin_lluvia:        int
    dias_con_lluvia:        int

    @classmethod
    def from_dict(cls, d: dict) -> "ClimaPeriodo":
        return cls(
            temperatura_promedio=d.get("temperatura_promedio", 0),
            temperatura_max=d.get("temperatura_max", 0),
            temperatura_min=d.get("temperatura_min", 0),
            precipitacion_promedio=d.get("precipitacion_promedio", 0),
            precipitacion_total=d.get("precipitacion_total", 0),
            humedad_promedio=d.get("humedad_promedio", 0),
            dias_sin_lluvia=d.get("dias_sin_lluvia", 0),
            dias_con_lluvia=d.get("dias_con_lluvia", 0),
        )

    def to_dict(self) -> dict:
        return {
            "temperatura_promedio":   self.temperatura_promedio,
            "temperatura_max":        self.temperatura_max,
            "temperatura_min":        self.temperatura_min,
            "precipitacion_promedio": self.precipitacion_promedio,
            "precipitacion_total":    self.precipitacion_total,
            "humedad_promedio":       self.humedad_promedio,
            "dias_sin_lluvia":        self.dias_sin_lluvia,
            "dias_con_lluvia":        self.dias_con_lluvia,
        }


@dataclass
class AlertaModel:
    id:                 str
    tipo:               str
    severidad:          str
    departamento:       str
    titulo:             str
    mensaje:            str
    cultivos_afectados: list[str]
    variables:          dict[str, float]
    recomendacion:      str
    score:              int
    fecha:              str
    activa:             bool = True


@dataclass
class RiskEvaluation:
    score:      float
    risk_level: str
    confidence: float
    message:    str


@dataclass
class YieldPrediction:
    departamento:         str
    cultivo:              str
    rendimiento_predicho: float
    nivel:                str
    anio:                 int
    area_sembrada:        float
    unidad:               str = "t/ha"


@dataclass
class EnsoRecord:
    anio:       int
    fase:       str
    intensidad: str
    oni:        float
    es_el_nino: bool
    es_la_nina: bool

    @property
    def impacto_colombia(self) -> str:
        if self.es_el_nino:
            return "Sequías"
        if self.es_la_nina:
            return "Lluvias excesivas"
        return "Normal"
