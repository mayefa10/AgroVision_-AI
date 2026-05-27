from enum import Enum

class RiskLevel(str, Enum):
    LOW      = "low"
    MEDIUM   = "medium"
    HIGH     = "high"
    CRITICAL = "critical"

class PredictionType(str, Enum):
    SEQUIA      = "sequia"
    INUNDACION  = "inundacion"
    HELADA      = "helada"
    RENDIMIENTO = "rendimiento_cultivo"

class AlertType(str, Enum):
    SEQUIA         = "sequia"
    INUNDACION     = "inundacion"
    HELADA         = "helada"
    ESTRES_TERMICO = "estres_termico"

class AlertSeverity(str, Enum):
    CRITICA = "critica"
    ALTA    = "alta"
    MEDIA   = "media"
    BAJA    = "baja"