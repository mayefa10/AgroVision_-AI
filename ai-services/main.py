"""
AgroVision AI — AI Services v0.2.0
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
import numpy as np
import uvicorn
from services.nasa_service import get_nasa_climate

import os

from data_pipeline import (
    fetch_eva_data,
    fetch_eva_summary,
    fetch_nasa_power,
    fetch_openweather,
    fetch_full_pipeline,
    DEPARTAMENTOS,
)
from dane_module import fetch_divipola_geo, fetch_dane_municipios_join, lookup_municipio

app = FastAPI(
    title="AgroVision AI — Services",
    description="""
Servicio de predicciones e IA para AgroVision.

**Fuentes de datos:**
- 🌾 EVA (datos.gov.co) — Evaluaciones Agropecuarias Municipales 2019-2024
- 🛰️ NASA POWER — Datos agroclimáticos históricos (sin API key)
- 🌤️ OpenWeather — Clima en tiempo real
- 🗺️ DANE DIVIPOLA — Georreferenciación oficial municipios
    """,
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

class PredictRiskRequest(BaseModel):
    region_code:     str             = Field(..., example="05001")
    prediction_type: PredictionType  = PredictionType.SEQUIA
    temperatura:     float           = Field(..., ge=-10, le=50, example=28.5)
    humedad:         float           = Field(..., ge=0, le=100, example=65.0)
    precipitacion:   float           = Field(..., ge=0, example=12.0)
    viento:          Optional[float] = Field(None, example=8.5)
    altitud:         Optional[float] = Field(None, example=1500.0)

class PredictRiskResponse(BaseModel):
    region_code:     str
    prediction_type: str
    risk:            RiskLevel
    confidence:      float
    message:         str
    variables_used:  dict

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

@app.get("/", tags=["Health"])
def root():
    return {"service": "AgroVision AI", "version": "0.2.0", "status": "running"}

@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}

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
        region_code=req.region_code,
        prediction_type=req.prediction_type.value,
        risk=risk_level,
        confidence=confidence,
        message=messages[risk_level],
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

@app.get("/eva/data", tags=["EVA"])
async def eva_data(
    departamento: Optional[str] = Query(None, example="ANTIOQUIA"),
    cultivo:      Optional[str] = Query(None, example="MAIZ"),
    anio:         Optional[int] = Query(None, example=2023),
    limit:        int           = Query(500, le=5000),
):
    return await fetch_eva_data(departamento=departamento, cultivo=cultivo, anio=anio, limit=limit)

@app.get("/eva/cultivos", tags=["EVA"])
async def eva_cultivos(departamento: Optional[str] = Query(None)):
    result = await fetch_eva_data(departamento=departamento, limit=5000)
    if not result.get("success"):
        return result
    cultivos = list({r.get("cultivo", "") for r in result.get("data", []) if r.get("cultivo")})
    return {"success": True, "total": len(cultivos), "cultivos": sorted(cultivos)}

@app.get("/clima/nasa/{departamento}", tags=["Clima"])
async def clima_nasa(departamento: str, days: int = Query(30, ge=7, le=365)):
    info = DEPARTAMENTOS.get(departamento.upper())
    if not info:
        raise HTTPException(status_code=404, detail=f"Departamento no encontrado")
    return await fetch_nasa_power(lat=info["lat"], lng=info["lng"], days=days, departamento=departamento.upper())

@app.get("/clima/nasa/coords", tags=["Clima"])
async def clima_nasa_coords(lat: float = Query(...), lng: float = Query(...), days: int = Query(30)):
    return await fetch_nasa_power(lat=lat, lng=lng, days=days)

@app.get("/clima/actual/{departamento}", tags=["Clima"])
async def clima_actual(departamento: str):
    info = DEPARTAMENTOS.get(departamento.upper())
    if not info:
        raise HTTPException(status_code=404, detail="Departamento no encontrado")
    return await fetch_openweather(info["capital"], departamento.upper())

@app.get("/dane/municipios", tags=["DANE"])
async def dane_municipios(departamento: Optional[str] = Query(None)):
    return await fetch_dane_municipios_join(departamento=departamento)

@app.get("/dane/lookup/{nombre}", tags=["DANE"])
async def dane_lookup(nombre: str):
    return await lookup_municipio(nombre)

@app.get("/pipeline/{departamento}", tags=["Pipeline"])
async def pipeline(departamento: str, cultivo: str = Query("MAIZ")):
    return await fetch_full_pipeline(departamento=departamento.upper(), cultivo=cultivo.upper())

@app.get("/clima/nasa/{departamento}")
def nasa_climate(departamento: str, days: int = 30):

    return get_nasa_climate(departamento, days)

@app.get("/departamentos", tags=["Regiones"])
def departamentos():
    return {"total": len(DEPARTAMENTOS),
            "departamentos": [{"nombre": k, "capital": v["capital"], "lat": v["lat"], "lng": v["lng"]}
                               for k, v in DEPARTAMENTOS.items()]}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)),
                reload=os.getenv("ENV") == "development")