# 🇨🇴 IA Colombia Platform

Plataforma de inteligencia artificial para **Agricultura y Desarrollo Sostenible** en Colombia,
basada en datos abiertos (IDEAM, DANE, datos.gov.co, OpenWeather, NASA POWER).

---

## 🏗️ Stack

| Capa        | Tecnología                              |
|-------------|------------------------------------------|
| Frontend    | Next.js · TypeScript · TailwindCSS · Recharts · Leaflet |
| Backend     | NestJS · Prisma ORM · PostgreSQL · JWT  |
| IA          | FastAPI · Pandas · Scikit-learn         |
| DevOps      | Docker · Docker Compose · GitHub        |

---

## 📁 Estructura

```
ia-colombia-platform/
├── frontend/          # Next.js app
├── backend/           # NestJS API + Prisma
│   └── prisma/
│       └── schema.prisma
├── ai-services/       # FastAPI + ML models
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── datasets/
│   ├── raw/
│   ├── processed/
│   └── notebooks/
├── docs/
├── docker-compose.yml
└── setup.sh
```

---

## 🚀 Inicio Rápido

### Opción A — Script automático (recomendado)

```bash
chmod +x setup.sh
./setup.sh
```

### Opción B — Manual paso a paso

#### 1. Base de datos

```bash
docker compose up -d
```

#### 2. Backend

```bash
cd backend
cp .env.example .env
npm install
npx prisma migrate dev --name init
npm run start:dev
```

#### 3. AI Services

```bash
cd ai-services
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

#### 4. Frontend

```bash
cd frontend
cp .env.local.example .env.local
npm install
npm run dev
```

---

## 🌐 URLs

| Servicio     | URL                         |
|--------------|-----------------------------|
| Frontend     | http://localhost:3000        |
| Backend API  | http://localhost:4000        |
| AI Service   | http://localhost:8000        |
| Swagger AI   | http://localhost:8000/docs   |
| PgAdmin      | http://localhost:5050        |

---

## 🤖 Endpoints IA

### `POST /predict-risk`

```json
// Request
{
  "region_code": "05001",
  "prediction_type": "sequia",
  "temperatura": 32.5,
  "humedad": 38.0,
  "precipitacion": 3.0,
  "altitud": 800
}

// Response
{
  "region_code": "05001",
  "prediction_type": "sequia",
  "risk": "high",
  "confidence": 0.78,
  "message": "Riesgo alto de sequia. Se recomienda activar protocolos preventivos.",
  "variables_used": { ... }
}
```

### `GET /regions/risk-summary`

Retorna resumen de riesgo para los 12 departamentos principales.

---

## 📊 Fuentes de Datos

| Fuente             | URL                                      | Uso                    |
|--------------------|------------------------------------------|------------------------|
| datos.gov.co       | https://www.datos.gov.co                 | Datasets nacionales    |
| IDEAM              | http://www.ideam.gov.co                  | Clima e hidrología     |
| DANE               | https://www.dane.gov.co                  | Datos socioeconómicos  |
| OpenWeather        | https://openweathermap.org/api           | Clima tiempo real      |
| NASA POWER         | https://power.larc.nasa.gov              | Datos agroclimáticos   |

---

## 🛠️ Módulos Backend (NestJS)

- `auth` — JWT login/registro
- `users` — Gestión de usuarios
- `dashboard` — Métricas y KPIs
- `datasets` — Ingesta y gestión de datos
- `predictions` — Integración con AI Service
- `alerts` — Sistema de alertas
- `maps` — Datos geoespaciales

---

## 🏆 MVP Checklist

- [ ] Login simple (JWT)
- [ ] Dashboard con gráficas (Recharts)
- [ ] Mapa interactivo (Leaflet)
- [ ] Datos abiertos reales (IDEAM / OpenWeather)
- [ ] Predicción IA básica (`/predict-risk`)
- [ ] Docker funcionando
- [ ] GitHub organizado

---

## 👥 Contribuir

```bash
git checkout -b feature/nombre-feature
git commit -m "feat: descripción"
git push origin feature/nombre-feature
```

```
AgroVision_AI
├─ .qodo
│  ├─ agents
│  └─ workflows
├─ ai-services
│  ├─ alertas.py
│  ├─ app
│  │  ├─ api
│  │  │  ├─ deps.py
│  │  │  ├─ main.py
│  │  │  ├─ routers
│  │  │  │  ├─ alerts.py
│  │  │  │  ├─ climate.py
│  │  │  │  ├─ dane.py
│  │  │  │  ├─ etl.py
│  │  │  │  ├─ eva.py
│  │  │  │  ├─ health.py
│  │  │  │  ├─ ml.py
│  │  │  │  ├─ predictions.py
│  │  │  │  └─ __init__.py
│  │  │  └─ __init__.py
│  │  ├─ config
│  │  │  ├─ constants.py
│  │  │  ├─ logging_config.py
│  │  │  ├─ settings.py
│  │  │  └─ __init__.py
│  │  ├─ domain
│  │  │  ├─ enums.py
│  │  │  ├─ models.py
│  │  │  ├─ schemas.py
│  │  │  └─ __init__.py
│  │  ├─ etl
│  │  │  ├─ cleaners
│  │  │  │  └─ eva_cleaner.py
│  │  │  ├─ loaders
│  │  │  │  └─ csv_loader.py
│  │  │  ├─ pipelines
│  │  │  │  └─ master_pipeline.py
│  │  │  ├─ transformers
│  │  │  │  └─ enso_transformer.py
│  │  │  └─ __init__.py
│  │  ├─ infrastructure
│  │  │  ├─ cache
│  │  │  │  └─ redis_client.py
│  │  │  ├─ clients
│  │  │  │  ├─ base_client.py
│  │  │  │  ├─ dane_client.py
│  │  │  │  ├─ eva_client.py
│  │  │  │  ├─ nasa_client.py
│  │  │  │  ├─ weather_client.py
│  │  │  │  └─ __init__.py
│  │  │  ├─ persistence
│  │  │  │  └─ dataset_storage.py
│  │  │  └─ __init__.py
│  │  ├─ ml
│  │  │  ├─ features
│  │  │  │  ├─ engineering.py
│  │  │  │  └─ selection.py
│  │  │  ├─ inference
│  │  │  │  └─ predictor.py
│  │  │  ├─ models
│  │  │  │  ├─ base.py
│  │  │  │  ├─ random_forest.py
│  │  │  │  └─ __init__.py
│  │  │  ├─ training
│  │  │  │  └─ trainer.py
│  │  │  └─ __init__.py
│  │  ├─ utils
│  │  │  ├─ dates.py
│  │  │  └─ __init__.py
│  │  └─ __init__.py
│  ├─ dane_module.py
│  ├─ data_pipeline.py
│  ├─ Dockerfile
│  ├─ etl_pipeline.py
│  ├─ main.py
│  ├─ ml_model.py
│  ├─ requirements.txt
│  ├─ services
│  │  ├─ alert_service.py
│  │  ├─ climate_service.py
│  │  ├─ etl_service.py
│  │  ├─ eva_service.py
│  │  ├─ ml_service.py
│  │  ├─ nasa_service.py
│  │  ├─ risk_service.py
│  │  └─ __init__.py
│  └─ tests
│     ├─ conftest.py
│     ├─ fixtures
│     │  ├─ mock_eva_response.json
│     │  └─ mock_nasa_response.json
│     ├─ integration
│     │  ├─ test_e2e_pipeline.py
│     │  └─ test_nasa_client.py
│     ├─ unit
│     │  ├─ test_eva_client.py
│     │  ├─ test_ml_predictor.py
│     │  └─ test_risk_service.py
│     └─ __init__.py
├─ backend
│  ├─ .prettierrc
│  ├─ Dockerfile
│  ├─ eslint.config.mjs
│  ├─ nest-cli.json
│  ├─ package-lock.json
│  ├─ package.json
│  ├─ prisma
│  │  ├─ migrations
│  │  │  ├─ 20260514212000_init
│  │  │  │  └─ migration.sql
│  │  │  └─ migration_lock.toml
│  │  └─ schema.prisma
│  ├─ README.md
│  ├─ src
│  │  ├─ alerts
│  │  │  └─ alerts.module.ts
│  │  ├─ app.controller.spec.ts
│  │  ├─ app.controller.ts
│  │  ├─ app.module.ts
│  │  ├─ app.service.ts
│  │  ├─ auth
│  │  │  └─ auth.module.ts
│  │  ├─ dashboard
│  │  │  └─ dashboard.module.ts
│  │  ├─ datasets
│  │  │  └─ datasets.module.ts
│  │  ├─ main.ts
│  │  ├─ maps
│  │  │  └─ maps.module.ts
│  │  ├─ predictions
│  │  │  └─ predictions.module.ts
│  │  └─ users
│  │     └─ users.module.ts
│  ├─ test
│  │  ├─ app.e2e-spec.ts
│  │  └─ jest-e2e.json
│  ├─ tsconfig.build.json
│  └─ tsconfig.json
├─ docker-compose.yml
├─ frontend
│  ├─ AGENTS.md
│  ├─ CLAUDE.md
│  ├─ Dockerfile
│  ├─ eslint.config.mjs
│  ├─ next.config.ts
│  ├─ package-lock.json
│  ├─ package.json
│  ├─ postcss.config.mjs
│  ├─ public
│  │  ├─ file.svg
│  │  ├─ globe.svg
│  │  ├─ next.svg
│  │  ├─ vercel.svg
│  │  └─ window.svg
│  ├─ README.md
│  ├─ src
│  │  ├─ app
│  │  │  ├─ dashboard
│  │  │  │  └─ page.tsx
│  │  │  ├─ globals.css
│  │  │  ├─ layout.tsx
│  │  │  └─ page.tsx
│  │  ├─ components
│  │  │  ├─ features
│  │  │  │  ├─ AgricolaSection.tsx
│  │  │  │  ├─ AlertasSection.tsx
│  │  │  │  ├─ charts
│  │  │  │  │  ├─ ClimateAreaChart.tsx
│  │  │  │  │  └─ RiskBarChart.tsx
│  │  │  │  ├─ ClimaSection.tsx
│  │  │  │  ├─ map
│  │  │  │  │  ├─ ColombiaMap.tsx
│  │  │  │  │  └─ MapSection.tsx
│  │  │  │  ├─ OverviewSection.tsx
│  │  │  │  └─ PrediccionSection.tsx
│  │  │  └─ ui
│  │  │     ├─ Badge.tsx
│  │  │     ├─ Button.tsx
│  │  │     ├─ Card.tsx
│  │  │     ├─ KpiCard.tsx
│  │  │     ├─ SectionHeader.tsx
│  │  │     ├─ Sidebar.tsx
│  │  │     ├─ Table.tsx
│  │  │     └─ Tabs.tsx
│  │  ├─ hooks
│  │  │  ├─ useAlertas.ts
│  │  │  ├─ useEvaData.ts
│  │  │  ├─ useMlModel.ts
│  │  │  ├─ useNasaData.ts
│  │  │  ├─ usePrediction.ts
│  │  │  └─ useRegions.ts
│  │  ├─ lib
│  │  │  ├─ api.ts
│  │  │  ├─ constants.ts
│  │  │  └─ utils.ts
│  │  ├─ services
│  │  │  └─ climate.service.ts
│  │  ├─ styles
│  │  │  └─ animations.css
│  │  └─ types
│  │     └─ index.ts
│  └─ tsconfig.json
├─ README.md
└─ setup.sh

```