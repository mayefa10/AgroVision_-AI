# Guía de validación para evaluadores — AgroVision AI

Esta guía permite al evaluador verificar de forma independiente todos los componentes del proyecto.

## 1. Verificar el repositorio

```
https://github.com/mayefa10/AgroVision_-AI
```

Estructura esperada:
```
├── README.md          ← Ficha técnica completa
├── docs/              ← Documentación técnica
├── notebooks/         ← Análisis exploratorio y modelo
├── RECURSOS/          ← Presentación PDF y PPTX
├── ai-services/       ← Código fuente backend IA
├── frontend/          ← Código fuente dashboard
└── docker-compose.yml ← Orquestación de contenedores
```

## 2. Ejecutar el sistema localmente

### Prerrequisitos
- Docker Desktop instalado
- Git

### Pasos

```bash
# 1. Clonar
git clone https://github.com/mayefa10/AgroVision_-AI.git
cd AgroVision_-AI

# 2. Configurar
cp ai-services/.env.example ai-services/.env
# Editar .env y agregar OPENWEATHER_API_KEY

# 3. Levantar
docker compose up --build

# 4. Verificar que levantó
docker compose ps
# Todos los servicios deben estar "Up"
```

### URLs de verificación

| Componente | URL | Qué verificar |
|------------|-----|---------------|
| Landing page | http://localhost:3000 | Carga correctamente |
| Dashboard | http://localhost:3000/dashboard | 8 secciones visibles |
| API docs | http://localhost:8000/docs | Endpoints documentados |
| Health check | http://localhost:8000/health | `{"status": "ok"}` |

## 3. Verificar los datos

### EVA (datos.gov.co)
```
http://localhost:8000/eva?departamento=ANTIOQUIA&limit=5
```
Debe retornar registros con: municipio, cultivo, rendimiento, anio

### NASA POWER
```
http://localhost:8000/clima/ANTIOQUIA?days=7
```
Debe retornar: temperatura, precipitacion, humedad de los últimos 7 días

### NOAA ENSO
```
http://localhost:8000/enso
```
Debe retornar: fase actual (El Niño/La Niña/Neutro), índice ONI, probabilidades

### Departamentos dinámicos
```
http://localhost:8000/eva/departamentos
```
Debe retornar lista de 32 departamentos con total de registros cada uno

## 4. Verificar el modelo ML

### Entrenar el modelo
```bash
curl.exe -X POST http://localhost:8000/ml/train
# Tarda 3-5 minutos — descarga 20,000 registros EVA
```

### Verificar métricas
```
http://localhost:8000/ml/metrics
```
Debe retornar:
```json
{
  "mae": 2.931,
  "r2": 0.697,
  "registros_totales": 12177,
  "feature_importance": { ... }
}
```

### Hacer una predicción
```bash
curl.exe -X POST http://localhost:8000/ml/predict-rendimiento \
  -H "Content-Type: application/json" \
  -d "{\"departamento\": \"ANTIOQUIA\", \"cultivo\": \"MAIZ\", \"grupo_cultivo\": \"CEREALES Y LEGUMINOSAS\", \"area_sembrada\": 100, \"anio\": 2024, \"periodo\": 1}"
```

## 5. Verificar notebooks

Abrir en Jupyter o VS Code:

```bash
cd notebooks
jupyter notebook
```

| Notebook | Qué verifica |
|----------|-------------|
| `01_EDA_exploracion_datos.ipynb` | Análisis exploratorio EVA |
| `02_limpieza_transformacion.ipynb` | Pipeline de limpieza |
| `03_analisis_descriptivo.ipynb` | Estadísticas y correlaciones |
| `04_modelo_predictivo.ipynb` | Entrenamiento y métricas |

## 6. Verificar cache PostgreSQL

```bash
# Ver datos cacheados en la BD
docker exec agrovision_db psql -U postgres -d agrovision \
  -c "SELECT name, source, \"fetchedAt\" FROM datasets ORDER BY \"fetchedAt\" DESC LIMIT 10;"
```

## 7. Preguntas frecuentes del evaluador

**¿Cómo sé que los datos vienen de fuentes reales y no son hardcodeados?**
Los clientes HTTP en `ai-services/app/infrastructure/clients/` muestran las llamadas reales a cada API. Los logs de Docker muestran `Cache MISS` en la primera llamada y `Cache HIT` en las siguientes.

**¿Cómo verifico que el modelo usa 12 variables?**
El endpoint `/ml/metrics` retorna `feature_importance` con exactamente 12 keys.

**¿El modelo es reproducible?**
Sí: `random_state=42` en el split y el RandomForestRegressor garantizan resultados idénticos con los mismos datos.
