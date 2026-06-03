"""AgroVision AI — Enumeraciones del dominio."""
from __future__ import annotations

from enum import Enum


class RiskLevel(str, Enum):
    LOW      = "low"
    MEDIUM   = "medium"
    HIGH     = "high"
    CRITICAL = "critical"


class AlertType(str, Enum):
    SEQUIA         = "sequia"
    INUNDACION     = "inundacion"
    HELADA         = "helada"
    ESTRES_TERMICO = "estres_termico"


class AlertSeverity(str, Enum):
    MEDIA   = "media"
    ALTA    = "alta"
    CRITICA = "critica"


class PredictionType(str, Enum):
    SEQUIA            = "sequia"
    INUNDACION        = "inundacion"
    HELADA            = "helada"
    RENDIMIENTO       = "rendimiento_cultivo"


class EnsoPhase(str, Enum):
    EL_NINO = "El Nino"
    LA_NINA = "La Nina"
    NEUTRO  = "Neutro"


class YieldLevel(str, Enum):
    BAJO      = "bajo"
    REGULAR   = "regular"
    BUENO     = "bueno"
    EXCELENTE = "excelente"
