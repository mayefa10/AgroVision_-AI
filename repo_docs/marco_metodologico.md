# Marco metodológico — CRISP-ML

AgroVision AI sigue el proceso **CRISP-ML (Cross-Industry Standard Process for Machine Learning)**.

## Fase 1: Comprensión del negocio

**Objetivo de negocio**: Reducir pérdidas agrícolas por eventos climáticos extremos mediante predicción temprana de rendimiento y alertas automáticas.

**Objetivo ML**: Predecir rendimiento agrícola (t/ha) por cultivo y departamento con MAE < 4 t/ha y R² > 0.6.

**Criterios de éxito**:
- Modelo entrenado con datos reales EVA 2019-2024
- Cobertura mínima: 20 departamentos, 10 cultivos
- Tiempo de respuesta < 2 segundos por predicción

## Fase 2: Comprensión de los datos

### Fuentes integradas
| Dataset | Registros | Variables | Calidad |
|---------|-----------|-----------|---------|
| EVA (datos.gov.co) | 145,000+ | 15 columnas | Alta (oficial UPRA) |
| NASA POWER | Diario/Anual | 5 variables climáticas | Alta (NASA) |
| NOAA ONI | Trimestral | 1 índice | Alta (NOAA) |
| OpenWeather | Tiempo real | 8 variables | Alta |
| DANE DIVIPOLA | ~1,100 municipios | Geografía | Alta |

### Análisis exploratorio (EDA)
Ver `notebooks/01_EDA_exploracion_datos.ipynb`

## Fase 3: Preparación de los datos

### Pipeline de limpieza
1. **Extracción**: Descarga paginada desde APIs Socrata y REST
2. **Limpieza**:
   - Filtro: `rendimiento IS NOT NULL AND rendimiento > 0`
   - Umbral: `rendimiento < 50 t/ha` (outliers agronómicos)
   - Nulos: `area_cosechada` imputado con `area_sembrada`
   - Nulos en métricas 2024: mantener como `null`, mostrar "—"
3. **Deduplicación**: por `municipio + cultivo + anio + periodo`
4. **Transformación**:
   - `LabelEncoder` para variables categóricas
   - `ratio_cosecha = area_cosechada / area_sembrada`
   - `rendimiento_hist_prom` = media histórica por depto/cultivo
   - `oni_index` desde tabla histórica NOAA integrada
   - `riesgo_climatico_enc` encoding ordinal ENSO

Ver `notebooks/02_limpieza_transformacion.ipynb`

## Fase 4: Modelado

### Algoritmo seleccionado: Random Forest Regressor

**Justificación**:
- Maneja bien variables categóricas codificadas
- Robusto a outliers
- Interpretable (feature importance)
- No requiere normalización de variables numéricas

### Hiperparámetros
```python
RandomForestRegressor(
    n_estimators=100,
    random_state=42
)
```

### Features (12 variables)
```
departamento_enc, cultivo_enc, grupo_cultivo_enc,
area_sembrada, anio, periodo_num,
municipio_enc, area_cosechada, ratio_cosecha,
rendimiento_hist_prom, oni_index, riesgo_climatico_enc
```

### Split de validación
- 80% entrenamiento / 20% prueba
- `random_state=42` para reproducibilidad

Ver `notebooks/04_modelo_predictivo.ipynb`

## Fase 5: Evaluación

### Métricas obtenidas
| Métrica | Valor | Interpretación |
|---------|-------|----------------|
| MAE | 2.93 t/ha | Error promedio por predicción |
| R² | 0.697 | 69.7% de varianza explicada |
| Registros train | 9,741 | 80% del dataset limpio |
| Registros test | 2,436 | 20% del dataset limpio |

### Variable más influyente
`rendimiento_hist_prom` (81%) — el promedio histórico por departamento/cultivo es el mejor predictor, lo que tiene sentido agronómico.

## Fase 6: Despliegue

- Modelo serializado en `models/rendimiento_model.pkl`
- Encoders en `models/encoders.pkl`
- Métricas en `models/metrics.json`
- API de predicción: `POST /ml/predict-rendimiento`
- Reentrenamiento: `POST /ml/train`
- Persistencia: volumen Docker `./models:/app/models`
