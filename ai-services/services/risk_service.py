"""AgroVision AI — Servicio de cálculo de riesgo climático."""
# Copyright (C) 2026 July Mayerly Quintero Farfán

from __future__ import annotations

import numpy as np

from app.domain.enums import PredictionType, RiskLevel
from app.domain.schemas import PredictRiskRequest


def calculate_risk(req: PredictRiskRequest) -> tuple[RiskLevel, float]:
    """
    Calcula nivel de riesgo y confianza a partir de variables climáticas.
    Retorna (RiskLevel, confidence).
    """
    score = 0.0

    if req.prediction_type == PredictionType.SEQUIA:
        if req.precipitacion < 5:    score += 0.40
        elif req.precipitacion < 15: score += 0.20
        if req.humedad < 40:         score += 0.30
        elif req.humedad < 55:       score += 0.15
        if req.temperatura > 32:     score += 0.30
        elif req.temperatura > 28:   score += 0.15

    elif req.prediction_type == PredictionType.INUNDACION:
        if req.precipitacion > 80:   score += 0.50
        elif req.precipitacion > 40: score += 0.30
        if req.humedad > 90:         score += 0.30
        elif req.humedad > 80:       score += 0.15

    elif req.prediction_type == PredictionType.HELADA:
        if req.temperatura < 4:      score += 0.50
        elif req.temperatura < 8:    score += 0.25
        if req.altitud and req.altitud > 2500: score += 0.30
        elif req.altitud and req.altitud > 1800: score += 0.15

    score = min(score, 1.0)

    if score >= 0.75:   level = RiskLevel.CRITICAL
    elif score >= 0.50: level = RiskLevel.HIGH
    elif score >= 0.25: level = RiskLevel.MEDIUM
    else:               level = RiskLevel.LOW

    # Confianza: base 70% ± pequeña variación aleatoria reproducible
    rng        = np.random.default_rng(seed=int(score * 1000))
    confidence = round(float(np.clip(0.70 + rng.uniform(-0.05, 0.10), 0.60, 0.95)), 2)

    return level, confidence


RISK_MESSAGES: dict[RiskLevel, str] = {
    RiskLevel.LOW:      "Condiciones normales. Sin riesgo detectado.",
    RiskLevel.MEDIUM:   "Riesgo moderado. Se recomienda monitoreo.",
    RiskLevel.HIGH:     "Riesgo alto. Activar protocolos preventivos.",
    RiskLevel.CRITICAL: "RIESGO CRÍTICO. Acción inmediata requerida.",
}

STATIC_RISK_SUMMARY = [
    {"region": "Antioquia",    "code": "05", "risk": "medium",   "lat": 6.2442,  "lng": -75.5812},
    {"region": "Bolívar",      "code": "13", "risk": "high",     "lat": 8.6706,  "lng": -74.0328},
    {"region": "Chocó",        "code": "27", "risk": "critical", "lat": 5.6920,  "lng": -76.6583},
    {"region": "Córdoba",      "code": "23", "risk": "high",     "lat": 8.0520,  "lng": -75.5735},
    {"region": "Cundinamarca", "code": "25", "risk": "low",      "lat": 4.6097,  "lng": -74.0817},
    {"region": "Guajira",      "code": "44", "risk": "critical", "lat": 11.5444, "lng": -72.9072},
    {"region": "Magdalena",    "code": "47", "risk": "high",     "lat": 10.4195, "lng": -74.4061},
    {"region": "Santander",    "code": "68", "risk": "low",      "lat": 6.6437,  "lng": -73.6536},
    {"region": "Tolima",       "code": "73", "risk": "medium",   "lat": 4.0925,  "lng": -75.1545},
    {"region": "Valle",        "code": "76", "risk": "low",      "lat": 3.8509,  "lng": -76.4919},
]
