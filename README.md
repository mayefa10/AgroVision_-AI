
# 🌾 AgroVision AI

**Plataforma de Inteligencia Agroclimática para Colombia**

> Concurso Datos al Ecosistema 2026 – Ministerio TIC · ID 31 July Quintero

[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)](https://www.docker.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-16-black?logo=next.js)](https://nextjs.org/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python)](https://python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)](https://postgresql.org/)

---

## 📋 Descripción

AgroVision AI es una plataforma de inteligencia artificial aplicada a la agricultura colombiana que integra **5 fuentes de datos abiertos** para generar predicciones de riesgo climático, alertas automáticas y escenarios de impacto ENSO por cultivo y departamento.

El sistema conecta datos históricos de producción agrícola (EVA), clima satelital (NASA POWER), fenómeno ENSO en tiempo real (NOAA/CPC), clima actual (OpenWeather) y geografía administrativa (DANE DIVIPOLA) en un dashboard interactivo con 8 módulos especializados.

---

## 🎯 Problema que resuelve

- **Información fragmentada**: productores rurales no acceden a datos climáticos y agrícolas consolidados
- **Sin predicción de riesgos**: no existen herramientas públicas que conecten ENSO con impactos reales por cultivo
- **Alertas tardías**: las alertas climáticas no llegan oportunamente, generando pérdidas evitables

---

## 🚀 Características principales

| Módulo | Descripción | Fuente |
|--------|-------------|--------|
| 🌦️ **Clima NASA** | Histórico 14-30 días por departamento | NASA POWER |
| 🌤️ **Tiempo Real** | Temperatura, humedad, viento actuales | OpenWeather |
| 🌊 **Monitor ENSO** | Índice ONI real + probabilidades + gráfica histórica | NOAA/CPC |
| 🌾 **Datos EVA** | 145k+ evaluaciones agropecuarias 2019-2024 | datos.gov.co |
| 🔔 **Alertas** | Sequía, inundación, helada, estrés térmico automáticas | NASA POWER |
| 🤖 **Escenarios IA** | El Niño/La Niña con impacto % por cultivo y región | NOAA + ML |
| 🗺️ **Mapa de Riesgo** | Visualización geográfica nacional | NASA + DANE |
| 📊 **Predicción IA** | Riesgo climático por región en tiempo real | Random Forest |

---

## 🤖 Modelo de Machine Learning

- **Algoritmo**: Random Forest Regressor (scikit-learn)
- **Target**: Rendimiento agrícola (t/ha)
- **Registros de entrenamiento**: 12,177 únicos (deduplicados)
- **MAE**: ±2.93 t/ha
- **R²**: 0.697 (69.7% de varianza explicada)
- **Features (12 variables)**:

```
departamento_enc    cultivo_enc         grupo_cultivo_enc
area_sembrada       anio                periodo_num
municipio_enc       area_cosechada      ratio_cosecha
rendimiento_hist_prom  oni_index        riesgo_climatico_enc
```

---

## 📊 Fuentes de datos

| Fuente | Dataset | Registros | Cobertura |
|--------|---------|-----------|-----------|
| **EVA** (datos.gov.co) | `uejq-wxrr` | 145,000+ | 32 departamentos · 2019-2024 |
| **NASA POWER** | API LARC | Diario | Nacional · Variables climáticas |
| **NOAA/CPC** | ONI Index | Trimestral | Global · ENSO real |
| **OpenWeather** | Current Weather | Tiempo real | 32 capitales |
| **DANE DIVIPOLA** | `gdxc-w37w` | Municipios | Nacional |

### Calidad de datos
- ✅ **Precisión**: fuente oficial UPRA/MinAgricultura
- ✅ **Completitud**: 32 departamentos, cobertura nacional
- ✅ **Unicidad**: deduplicación por municipio + cultivo + año + periodo
- ✅ **Validez**: filtro rendimiento > 0, nulos como `—` no `0 ha`
- ✅ **Coherencia**: normalización de columnas, umbral rendimiento < 50 t/ha
- ⚡ **Puntualidad**: cache PostgreSQL con TTL por fuente (EVA: 24h, NASA: 6h, OpenWeather: 1h)

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────┐
│                   Frontend (Next.js 16)              │
│         TypeScript · TailwindCSS · Recharts          │
└────────────────────┬────────────────────────────────┘
                     │ HTTP
┌────────────────────▼────────────────────────────────┐
│              Backend IA (FastAPI · Python 3.12)      │
│   EVA Client · NASA Client · NOAA Client · ML Model  │
│         Cache PostgreSQL (asyncpg · TTL)             │
└──────┬──────────────────────────────────┬────────────┘
       │                                  │
┌──────▼──────┐                  ┌────────▼────────────┐
│  PostgreSQL  │                  │  APIs Externas      │
│  (cache +   │                  │  EVA · NASA · NOAA  │
│   auth)     │                  │  OpenWeather · DANE  │
└─────────────┘                  └─────────────────────┘
┌─────────────────────────────────────────────────────┐
│              Backend (NestJS · Prisma ORM)           │
│              Autenticación JWT · PostgreSQL          │
└─────────────────────────────────────────────────────┘
```

### Stack tecnológico

| Capa | Tecnología |
|------|-----------|
| Frontend | Next.js 16, TypeScript, TailwindCSS, Recharts |
| Backend IA | FastAPI, Python 3.12, scikit-learn, pandas, asyncpg |
| Backend Auth | NestJS, Prisma ORM, JWT |
| Base de datos | PostgreSQL 16 |
| Infraestructura | Docker Compose (5 contenedores) |

---

## 🛠️ Instalación y uso

### Prerequisitos
- Docker Desktop instalado
- Git

### 1. Clonar el repositorio

```bash
git clone https://github.com/mayefa10/AgroVision_-AI.git
cd AgroVision_-AI
```

### 2. Configurar variables de entorno

```bash
# Crear archivo de configuración
cp ai-services/.env.example ai-services/.env
```

Editar `ai-services/.env`:

```env
ENV=development
PORT=8000
OPENWEATHER_API_KEY=tu_api_key_aqui   # Gratis en openweathermap.org
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/agrovision
```

### 3. Levantar el sistema

```bash
docker compose up --build
```

### 4. Entrenar el modelo ML

Una vez que los contenedores estén corriendo, entrenar el modelo:

```bash
# Opción A — desde la terminal
curl.exe -X POST http://localhost:8000/ml/train

# Opción B — desde el navegador
# Abrir http://localhost:8000/docs → POST /ml/train → Execute
```

El entrenamiento descarga ~20,000 registros EVA y tarda 3-5 minutos.

### 5. Acceder a la aplicación

| Servicio | URL |
|---------|-----|
| Landing page | http://localhost:3000 |
| Dashboard | http://localhost:3000/dashboard |
| API docs | http://localhost:8000/docs |
| pgAdmin | http://localhost:5050 |

---

## 📁 Estructura del proyecto

```
AgroVision_AI/
├── ai-services/              # Backend IA (FastAPI + ML)
│   ├── app/
│   │   ├── api/routers/      # Endpoints: EVA, NASA, ENSO, OpenWeather, ML
│   │   ├── infrastructure/
│   │   │   ├── clients/      # EVA, NASA, NOAA, OpenWeather, DANE
│   │   │   └── persistence/  # Cache PostgreSQL (asyncpg)
│   │   ├── ml/
│   │   │   ├── features/     # Feature engineering (12 variables)
│   │   │   ├── models/       # Random Forest
│   │   │   ├── training/     # Pipeline de entrenamiento
│   │   │   └── inference/    # Predictor con LRU cache
│   │   └── config/           # Settings, constantes, logging
│   └── services/             # Fachada de servicios
├── backend/                  # Backend Auth (NestJS + Prisma)
│   └── prisma/               # Schema PostgreSQL
├── frontend/                 # Dashboard (Next.js)
│   └── src/
│       ├── app/              # Páginas: landing, dashboard
│       ├── components/       # UI components + secciones
│       └── hooks/            # Data fetching hooks
├── models/                   # Modelo ML entrenado (.pkl) — persistente
├── docs/                     # Presentación PDF y PPTX
└── docker-compose.yml
```

---

## 🔌 API Endpoints principales

```
GET  /health                          # Estado del sistema
GET  /eva?departamento=ANTIOQUIA      # Datos EVA con filtros
GET  /eva/departamentos               # Departamentos con datos reales
GET  /clima/{departamento}            # Clima NASA POWER
GET  /openweather/{departamento}      # Clima actual OpenWeather
GET  /enso                            # Estado ENSO actual (NOAA)
GET  /escenarios?departamento=&cultivo= # Escenarios IA
GET  /alertas/{departamento}          # Alertas climáticas
POST /ml/train                        # Entrenar modelo ML
GET  /ml/metrics                      # Métricas del modelo
POST /ml/predict-rendimiento          # Predecir rendimiento
```

---

## 📈 Riesgos y mitigaciones IA

| Riesgo | Nivel | Mitigación |
|--------|-------|-----------|
| Alucinación del modelo | Bajo | Random Forest no inventa — interpola entre datos reales |
| Cambios en fuente externa | Medio | `fetched_at` en cache + TTL + log de cada sync |
| Pérdida de información | Bajo | Modelo .pkl persistido en volumen Docker `./models/` |
| Sesgo por cultivos dominantes | Medio | Feature importance visible en dashboard |
| Dependencia APIs externas | Bajo | Cache PostgreSQL como fallback si APIs fallan |

---

## 📄 Presentación

La presentación oficial del proyecto para el concurso está disponible en la carpeta [`/docs`](./docs/):

- `AgroVision_AI_Concurso.pdf` — Presentación en PDF
- `AgroVision_AI_Concurso.pptx` — Presentación editable

---

## 👤 Autora

**Mayerly Quintero Farfán**
ID 31 July · Concurso Datos al Ecosistema 2026 · Ministerio TIC

---

## 📜 Licencia

MIT License · Datos abiertos · Hecho en Colombia 🇨🇴
