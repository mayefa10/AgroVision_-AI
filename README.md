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
