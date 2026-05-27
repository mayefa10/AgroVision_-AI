"""
AgroVision AI — Entry point
Mantiene compatibilidad con los módulos existentes durante la migración.
"""
# Importar app nueva (nueva arquitectura)
from app.api.main import create_app

# Módulos legacy — se migrarán gradualmente
from data_pipeline import (
    fetch_eva_data, fetch_eva_summary, fetch_nasa_power,
    fetch_openweather, fetch_full_pipeline, DEPARTAMENTOS,
)
from dane_module import fetch_divipola_geo, fetch_dane_municipios_join, lookup_municipio
from ml_model import train_model, predict_rendimiento
from alertas import generar_alertas_departamento, generar_alertas_nacional
from etl_pipeline import construir_dataset_maestro, ENSO_HISTORICO

from fastapi import HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import datetime
import numpy as np
import uvicorn
import os

# Crear app con nueva arquitectura como base
app = create_app()

# ── Schemas legacy ────────────────────────────────────────

class RiskLevel(str, Enum):
    LOW = "low"; MEDIUM = "medium"; HIGH = "high"; CRITICAL = "critical"

class PredictionType(str, Enum):
    SEQUIA = "sequia"; INUNDACION = "inundacion"
    HELADA = "helada"; RENDIMIENTO = "rendimiento_cultivo"

class PredictRiskRequest(BaseModel):
    region_code:     str             = Field(..., example="05001")
    prediction_type: PredictionType  = PredictionType.SEQUIA
    temperatura:     float           = Field(..., ge=-10, le=50, example=28.5)
    humedad:         float           = Field(..., ge=0, le=100, example=65.0)
    precipitacion:   float           = Field(..., ge=0, example=12.0)
    viento:          Optional[float] = Field(None, example=8.5)
    altitud:         Optional[float] = Field(None, example=1500.0)

class PredictRiskResponse(BaseModel):
    region_code: str; prediction_type: str; risk: RiskLevel
    confidence: float; message: str; variables_used: dict

class RendimientoRequest(BaseModel):
    departamento: str = "ANTIOQUIA"; cultivo: str = "MAIZ"
    grupo_cultivo: str = "CEREALES Y LEGUMINOSAS"
    area_sembrada: float = 100.0; anio: int = 2024; periodo: int = 1

# ── Lógica riesgo ─────────────────────────────────────────

def calculate_risk(req: PredictRiskRequest):
    score = 0.0
    if req.prediction_type == PredictionType.SEQUIA:
        if req.precipitacion < 5:    score += 0.4
        elif req.precipitacion < 15: score += 0.2
        if req.humedad < 40:         score += 0.3
        elif req.humedad < 55:       score += 0.15
        if req.temperatura > 32:     score += 0.3
        elif req.temperatura > 28:   score += 0.15
    elif req.prediction_type == PredictionType.INUNDACION:
        if req.precipitacion > 80:   score += 0.5
        elif req.precipitacion > 40: score += 0.3
        if req.humedad > 90:         score += 0.3
    elif req.prediction_type == PredictionType.HELADA:
        if req.temperatura < 4:      score += 0.5
        elif req.temperatura < 8:    score += 0.25
        if req.altitud and req.altitud > 2500: score += 0.3
    score = min(score, 1.0)
    if score >= 0.75:   level = RiskLevel.CRITICAL
    elif score >= 0.5:  level = RiskLevel.HIGH
    elif score >= 0.25: level = RiskLevel.MEDIUM
    else:               level = RiskLevel.LOW
    confidence = round(0.70 + np.random.uniform(-0.05, 0.10), 2)
    return level, confidence

# ── Endpoints legacy ──────────────────────────────────────

@app.post("/predict-risk", response_model=PredictRiskResponse, tags=["Predicciones"])
def predict_risk(req: PredictRiskRequest):
    risk_level, confidence = calculate_risk(req)
    messages = {
        RiskLevel.LOW:      f"Condiciones normales. Sin riesgo de {req.prediction_type.value}.",
        RiskLevel.MEDIUM:   f"Alerta. Monitorear {req.prediction_type.value}.",
        RiskLevel.HIGH:     f"Riesgo alto de {req.prediction_type.value}. Activar protocolos.",
        RiskLevel.CRITICAL: f"RIESGO CRÍTICO de {req.prediction_type.value}. Emergencia.",
    }
    return PredictRiskResponse(
        region_code=req.region_code, prediction_type=req.prediction_type.value,
        risk=risk_level, confidence=confidence, message=messages[risk_level],
        variables_used={"temperatura": req.temperatura, "humedad": req.humedad,
                        "precipitacion": req.precipitacion, "viento": req.viento, "altitud": req.altitud},
    )

@app.get("/regions/risk-summary", tags=["Regiones"])
def risk_summary():
    return {"data": [
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
    ]}

@app.get("/eva/summary", tags=["EVA"])
async def eva_summary():
    return await fetch_eva_summary()

@app.get("/dane/municipios", tags=["DANE"])
async def dane_municipios(departamento: Optional[str] = Query(None)):
    return await fetch_dane_municipios_join(departamento=departamento)

@app.get("/dane/lookup/{nombre}", tags=["DANE"])
async def dane_lookup(nombre: str):
    return await lookup_municipio(nombre)

@app.get("/pipeline/{departamento}", tags=["Pipeline"])
async def pipeline(departamento: str, cultivo: str = Query("MAIZ")):
    return await fetch_full_pipeline(departamento=departamento.upper(), cultivo=cultivo.upper())

@app.get("/departamentos", tags=["Regiones"])
def departamentos():
    return {"total": len(DEPARTAMENTOS),
            "departamentos": [{"nombre": k, "capital": v["capital"], "lat": v["lat"], "lng": v["lng"]}
                               for k, v in DEPARTAMENTOS.items()]}

@app.post("/ml/train", tags=["ML"])
async def ml_train():
    return await train_model()

@app.post("/ml/predict-rendimiento", tags=["ML"])
def ml_predict(req: RendimientoRequest):
    return predict_rendimiento(req.departamento, req.cultivo, req.grupo_cultivo,
                                req.area_sembrada, req.anio, req.periodo)

@app.get("/ml/status", tags=["ML"])
def ml_status():
    trained = os.path.exists("rendimiento_model.pkl")
    return {"model_trained": trained,
            "message": "Listo para predecir" if trained else "Llama a POST /ml/train"}

@app.get("/alertas/{departamento}", tags=["Alertas"])
async def alertas_departamento(departamento: str):
    return await generar_alertas_departamento(departamento)

@app.get("/alertas", tags=["Alertas"])
async def alertas_nacional():
    return await generar_alertas_nacional()

@app.post("/etl/build", tags=["ETL"])
async def etl_build(max_eva: int = 10000):
    return await construir_dataset_maestro(max_eva)

@app.get("/etl/enso", tags=["ETL"])
def etl_enso():
    return {"fuente": "NOAA ONI Index", "data": [
        {"anio": a, **v,
         "impacto_colombia": "Sequías" if v["fase"] == "El Nino" else "Lluvias excesivas" if v["fase"] == "La Nina" else "Normal"}
        for a, v in ENSO_HISTORICO.items()
    ]}

@app.get("/etl/enso/actual", tags=["ETL"])
def etl_enso_actual():
    anio = datetime.utcnow().year
    enso = ENSO_HISTORICO.get(anio, ENSO_HISTORICO.get(2024))
    return {"anio": anio, "fase": enso["fase"], "intensidad": enso["intensidad"],
            "oni_index": enso["oni"], "alerta": enso["fase"] != "Neutro",
            "mensaje": f"⚠️ Fase {enso['fase']} activa. ONI={enso['oni']}. " +
                       ("Riesgo sequías." if enso["fase"] == "El Nino" else
                        "Riesgo lluvias excesivas." if enso["fase"] == "La Nina" else "Condiciones normales.")}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)),
                reload=os.getenv("ENV") == "development")