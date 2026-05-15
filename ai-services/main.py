"""
IA Colombia Platform — AI Services
FastAPI entry point
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import pandas as pd
import numpy as np
from enum import Enum
import uvicorn
import os

# ── App ───────────────────────────────────────────────────

app = FastAPI(
    title="IA Colombia — AI Services",
    description="Servicio de predicciones e IA para la plataforma",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:4000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Schemas ───────────────────────────────────────────────

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

class PredictRiskRequest(BaseModel):
    region_code: str = Field(..., example="05001")         # Código DANE
    prediction_type: PredictionType = PredictionType.SEQUIA
    temperatura: float = Field(..., ge=-10, le=50, example=28.5)
    humedad: float = Field(..., ge=0, le=100, example=65.0)
    precipitacion: float = Field(..., ge=0, example=12.0)  # mm
    viento: Optional[float] = Field(None, ge=0, example=8.5)
    altitud: Optional[float] = Field(None, ge=0, example=1500.0)

class PredictRiskResponse(BaseModel):
    region_code: str
    prediction_type: str
    risk: RiskLevel
    confidence: float
    message: str
    variables_used: dict

# ── Lógica de Predicción (MVP) ────────────────────────────

def calculate_risk_score(req: PredictRiskRequest) -> tuple[float, RiskLevel]:
    """
    Modelo heurístico para el MVP.
    Reemplazar con scikit-learn entrenado cuando tengamos datasets reales.
    """
    score = 0.0

    if req.prediction_type == PredictionType.SEQUIA:
        # Factores de riesgo sequía
        if req.precipitacion < 5:
            score += 0.4
        elif req.precipitacion < 15:
            score += 0.2

        if req.humedad < 40:
            score += 0.3
        elif req.humedad < 55:
            score += 0.15

        if req.temperatura > 32:
            score += 0.3
        elif req.temperatura > 28:
            score += 0.15

    elif req.prediction_type == PredictionType.INUNDACION:
        if req.precipitacion > 80:
            score += 0.5
        elif req.precipitacion > 40:
            score += 0.3

        if req.humedad > 90:
            score += 0.3
        elif req.humedad > 75:
            score += 0.15

    elif req.prediction_type == PredictionType.HELADA:
        if req.temperatura < 4:
            score += 0.5
        elif req.temperatura < 8:
            score += 0.25

        if req.altitud and req.altitud > 2500:
            score += 0.3
        elif req.altitud and req.altitud > 1800:
            score += 0.1

    # Normalizar a [0, 1]
    score = min(score, 1.0)

    # Mapear a nivel de riesgo
    if score >= 0.75:
        level = RiskLevel.CRITICAL
    elif score >= 0.5:
        level = RiskLevel.HIGH
    elif score >= 0.25:
        level = RiskLevel.MEDIUM
    else:
        level = RiskLevel.LOW

    # Confidence simulada (mejorar con modelo real)
    confidence = round(0.70 + np.random.uniform(-0.05, 0.10), 2)

    return score, level, confidence

# ── Endpoints ─────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "service": "IA Colombia — AI Services",
        "version": "0.1.0",
        "status": "running",
        "endpoints": ["/predict-risk", "/health", "/docs"],
    }

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict-risk", response_model=PredictRiskResponse)
def predict_risk(req: PredictRiskRequest):
    """
    Predice el nivel de riesgo para una región y tipo de evento.

    **Tipos disponibles:** sequia | inundacion | helada | rendimiento_cultivo

    **Retorna:** low | medium | high | critical
    """
    try:
        score, risk_level, confidence = calculate_risk_score(req)

        messages = {
            RiskLevel.LOW: f"Condiciones normales. Sin riesgo significativo de {req.prediction_type.value}.",
            RiskLevel.MEDIUM: f"Condiciones de alerta. Monitorear variables para {req.prediction_type.value}.",
            RiskLevel.HIGH: f"Riesgo alto de {req.prediction_type.value}. Se recomienda activar protocolos preventivos.",
            RiskLevel.CRITICAL: f"RIESGO CRÍTICO de {req.prediction_type.value}. Activar emergencia inmediatamente.",
        }

        return PredictRiskResponse(
            region_code=req.region_code,
            prediction_type=req.prediction_type.value,
            risk=risk_level,
            confidence=confidence,
            message=messages[risk_level],
            variables_used={
                "temperatura": req.temperatura,
                "humedad": req.humedad,
                "precipitacion": req.precipitacion,
                "viento": req.viento,
                "altitud": req.altitud,
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/regions/risk-summary")
def risk_summary():
    """
    Retorna resumen de riesgo para los principales departamentos.
    (Demo data — reemplazar con consulta real a BD)
    """
    return {
        "data": [
            {"region": "Antioquia",  "code": "05", "risk": "medium",   "lat": 6.2442,  "lng": -75.5812},
            {"region": "Bolívar",    "code": "13", "risk": "high",     "lat": 8.6706,  "lng": -74.0328},
            {"region": "Cauca",      "code": "19", "risk": "medium",   "lat": 2.4448,  "lng": -76.6147},
            {"region": "Chocó",      "code": "27", "risk": "critical", "lat": 5.6920,  "lng": -76.6583},
            {"region": "Córdoba",    "code": "23", "risk": "high",     "lat": 8.0520,  "lng": -75.5735},
            {"region": "Cundinamarca","code":"25", "risk": "low",      "lat": 4.6097,  "lng": -74.0817},
            {"region": "Guajira",    "code": "44", "risk": "critical", "lat": 11.5444, "lng": -72.9072},
            {"region": "Magdalena",  "code": "47", "risk": "high",     "lat": 10.4195, "lng": -74.4061},
            {"region": "Nariño",     "code": "52", "risk": "medium",   "lat": 1.2136,  "lng": -77.2811},
            {"region": "Santander",  "code": "68", "risk": "low",      "lat": 6.6437,  "lng": -73.6536},
            {"region": "Tolima",     "code": "73", "risk": "medium",   "lat": 4.0925,  "lng": -75.1545},
            {"region": "Valle",      "code": "76", "risk": "low",      "lat": 3.8509,  "lng": -76.4919},
        ]
    }

# ── Run ───────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("ENV") == "development",
    )
