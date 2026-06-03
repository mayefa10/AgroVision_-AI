# AgroVision AI — ai-services

Microservicio FastAPI de inteligencia artificial para agricultura y desarrollo sostenible en Colombia.

---

## Arquitectura

```
ai-services/
├── main.py                        # Entry point → uvicorn
├── app/
│   ├── api/
│   │   ├── main.py                # Factory FastAPI + lifespan
│   │   ├── deps.py                # Dependencias (Depends)
│   │   └── routers/               # Un router por dominio
│   │       ├── predictions.py     # POST /predict-risk
│   │       ├── alerts.py          # GET  /alertas
│   │       ├── climate.py         # GET  /clima, /departamentos, /pipeline
│   │       ├── eva.py             # GET  /eva
│   │       ├── dane.py            # GET  /dane
│   │       ├── ml.py              # POST /ml/train, /ml/predict-rendimiento
│   │       ├── etl.py             # POST /etl/build, GET /etl/enso
│   │       └── health.py          # GET  /health
│   ├── config/
│   │   ├── constants.py           # Fuente única de verdad (coords, umbrales, ENSO)
│   │   ├── settings.py            # Pydantic-settings (env vars)
│   │   └── logging_config.py
│   ├── domain/
│   │   ├── enums.py               # RiskLevel, AlertType, YieldLevel…
│   │   ├── models.py              # Dataclasses internas de dominio
│   │   └── schemas.py             # Schemas Pydantic (request/response)
│   ├── infrastructure/
│   │   ├── clients/               # Clientes HTTP externos
│   │   │   ├── base_client.py     # BaseHttpClient con get_safe()
│   │   │   ├── nasa_client.py     # NASA POWER (daily + annual)
│   │   │   ├── eva_client.py      # EVA / datos.gov.co (Socrata)
│   │   │   ├── dane_client.py     # DIVIPOLA (geo + códigos)
│   │   │   └── weather_client.py  # OpenWeather
│   │   ├── cache/
│   │   │   └── redis_client.py    # CacheClient con fallback graceful
│   │   └── persistence/
│   │       └── dataset_storage.py # Guardar/cargar CSVs
│   ├── etl/
│   │   ├── cleaners/eva_cleaner.py
│   │   ├── loaders/csv_loader.py
│   │   ├── pipelines/master_pipeline.py
│   │   └── transformers/enso_transformer.py
│   ├── ml/
│   │   ├── features/engineering.py  # prepare_features + domain_feature_engineering
│   │   ├── features/selection.py
│   │   ├── models/random_forest.py  # AgroRandomForest
│   │   ├── training/trainer.py      # run_training()
│   │   └── inference/predictor.py   # predict_rendimiento() con @lru_cache
│   └── utils/dates.py
├── services/                      # Orquestación: une clientes + dominio
│   ├── alert_service.py
│   ├── climate_service.py
│   ├── etl_service.py
│   ├── eva_service.py
│   ├── ml_service.py
│   ├── nasa_service.py
│   └── risk_service.py
└── tests/
    ├── conftest.py                # Fixtures compartidas
    ├── fixtures/                  # Datos mock JSON
    ├── unit/                      # Tests sin I/O
    └── integration/               # Tests con mocks de red
```

---

## Inicio rápido

```bash
# 1. Variables de entorno
cp .env.example .env
# Editar .env y agregar OPENWEATHER_API_KEY

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Arrancar
uvicorn main:app --reload --port 8000
```

Con Docker:

```bash
docker build -t agrovision-ai .
docker run -p 8000:8000 --env-file .env agrovision-ai
```

---

## Endpoints principales

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET  | `/health` | Estado del servicio y modelo |
| POST | `/predict-risk` | Predicción de riesgo por variables climáticas |
| GET  | `/alertas/{departamento}` | Alertas para un departamento |
| GET  | `/alertas` | Alertas para todos los departamentos |
| GET  | `/departamentos` | Lista de departamentos con coordenadas |
| GET  | `/clima/{departamento}` | Datos NASA POWER para un departamento |
| GET  | `/pipeline/{departamento}` | EVA + NASA + OpenWeather combinados |
| GET  | `/eva/summary` | Resumen nacional de producción agrícola |
| GET  | `/dane/municipios` | Municipios con coordenadas DANE |
| POST | `/ml/train` | Entrenar modelo con datos EVA reales |
| POST | `/ml/predict-rendimiento` | Predicción de rendimiento (t/ha) |
| POST | `/etl/build` | Construir dataset maestro completo |
| GET  | `/etl/enso` | Índice ENSO histórico |
| GET  | `/docs` | Swagger UI interactivo |

---

## Tests

```bash
# Todos los tests
pytest

# Solo unitarios (sin red)
pytest tests/unit/ -m unit

# Con cobertura
pytest --cov=app --cov=services --cov-report=term-missing
```

---

## Fuentes de datos

| Fuente | URL | Uso |
|--------|-----|-----|
| EVA — datos.gov.co | https://www.datos.gov.co | Producción agrícola 2019-2024 |
| NASA POWER | https://power.larc.nasa.gov | Clima histórico y diario |
| OpenWeather | https://openweathermap.org/api | Clima en tiempo real |
| DANE DIVIPOLA | https://www.datos.gov.co | Georreferenciación municipal |
