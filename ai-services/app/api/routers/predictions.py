"""AgroVision AI — Router predicciones de riesgo."""
from __future__ import annotations

from fastapi import APIRouter

from app.domain.schemas import PredictRiskRequest, PredictRiskResponse
from services.risk_service import RISK_MESSAGES, STATIC_RISK_SUMMARY, calculate_risk

router = APIRouter(prefix="", tags=["Predicciones"])


@router.post("/predict-risk", response_model=PredictRiskResponse)
def predict_risk(req: PredictRiskRequest):
    """Calcula riesgo agroclimático a partir de variables de entrada."""
    risk_level, confidence = calculate_risk(req)
    msg = RISK_MESSAGES[risk_level].replace(
        "detectado", f"de {req.prediction_type.value} detectado"
    )
    return PredictRiskResponse(
        region_code=req.region_code,
        prediction_type=req.prediction_type.value,
        risk=risk_level,
        confidence=confidence,
        message=msg,
        variables_used={
            "temperatura":    req.temperatura,
            "humedad":        req.humedad,
            "precipitacion":  req.precipitacion,
            "viento":         req.viento,
            "altitud":        req.altitud,
        },
    )


@router.get("/regions/risk-summary", tags=["Regiones"])
def risk_summary():
    """Resumen estático de riesgo por departamento (para el mapa)."""
    return {"data": STATIC_RISK_SUMMARY}
