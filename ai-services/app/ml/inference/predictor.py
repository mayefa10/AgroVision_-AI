from fastapi import APIRouter

from domain.models import RiskPredictionRequest, RiskPredictionResponse
from services.risk_service import RiskService

router = APIRouter(prefix="/predict", tags=["Predicciones"])
risk_service = RiskService()


@router.post("/risk", response_model=RiskPredictionResponse)
def predict_risk(request: RiskPredictionRequest):
    level, confidence, message = risk_service.calculate(request)
    
    return RiskPredictionResponse(
        region_code=request.region_code,
        prediction_type=request.prediction_type.value,
        risk=level,
        confidence=confidence,
        message=message,
        variables_used={
            "temperatura": request.temperatura,
            "humedad": request.humedad,
            "precipitacion": request.precipitacion,
            "viento": request.viento,
            "altitud": request.altitud,
        },
    )