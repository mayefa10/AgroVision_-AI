# Conclusiones, limitaciones y próximos pasos

## Hallazgos principales

### 1. El rendimiento histórico es el mejor predictor
La variable `rendimiento_hist_prom` (promedio histórico por departamento/cultivo) explica el **81%** de la importancia en el modelo Random Forest. Esto confirma que los patrones históricos de producción son el mejor proxy para predicciones futuras bajo condiciones normales.

### 2. La granularidad municipal mejora el modelo
Agregar `municipio_enc` como feature mejoró el R² de 0.604 (6 variables) a 0.697 (12 variables), confirmando que existe variación significativa dentro de los departamentos que el modelo puede capturar.

### 3. El ENSO no aporta directamente al modelo ML
`oni_index` y `riesgo_climatico_enc` tienen importancia 0% en el Random Forest. Esto se debe a que el modelo ya captura el año (`anio`) y el promedio histórico absorbe el efecto ENSO indirectamente. Sin embargo, el ENSO sigue siendo clave en los **Escenarios IA** para comunicar impactos futuros.

### 4. Los datos de 2024 están incompletos en la fuente
Los registros de 2024 en EVA llegan con `area_sembrada` y `produccion` como `null` porque el Ministerio aún no cierra las campañas agrícolas al momento de la consulta. El sistema los maneja correctamente mostrando "—" en vez de "0 ha".

### 5. El cache PostgreSQL reduce la latencia en 95%
La primera consulta a EVA tarda ~3 segundos (llamada a datos.gov.co). Las consultas subsiguientes al mismo departamento tardan < 100ms desde el cache PostgreSQL.

## Limitaciones

| Limitación | Impacto | Mitigación |
|------------|---------|------------|
| Modelo no capta tendencia temporal (`anio=0` en importancia) | Predicciones no mejoran con el año | Explorar series temporales (LSTM) en siguiente versión |
| Cultivos con pocos registros tienen predicciones menos confiables | Quinua, mora, uchuva tienen alta varianza | Filtrar por n_muestras mínimo |
| ENSO no conecta directamente con rendimiento en el modelo | Escenarios IA usan impactos parametrizados | Cruzar EVA histórico con ONI anual para cuantificar impacto real |
| OpenWeather requiere API key de pago para alta frecuencia | Límite de 1,000 requests/día en free tier | Migrar a tier Pro o usar solo para demos |
| Los datos EVA se publican con retraso de 6-12 meses | Año 2024 incompleto | Integrar datos SIPSA para precios en tiempo real |

## Próximos pasos

### Corto plazo (1-3 meses)
- [ ] Integrar datos SIPSA (precios de alimentos) para correlacionar rendimiento con precios al productor
- [ ] Agregar modelo de clustering (K-Means) para segmentar municipios por perfil de riesgo agroclimático
- [ ] Implementar notificaciones push para alertas críticas

### Mediano plazo (3-6 meses)
- [ ] Migrar modelo a gradient boosting (XGBoost) para mejorar R² a > 0.80
- [ ] Integrar datos de suelos (IGAC) como feature adicional
- [ ] Desarrollar módulo de series temporales para proyecciones a 6 meses

### Largo plazo (6-12 meses)
- [ ] Despliegue en producción con Railway/Render
- [ ] Aplicación móvil para productores rurales
- [ ] Integración con IDEAM para datos hidrometeorológicos oficiales
- [ ] Modelo de recomendación de cultivos por municipio basado en condiciones actuales

## Impacto potencial

Con cobertura en 32 departamentos y 145,000+ evaluaciones integradas, AgroVision AI tiene potencial para apoyar las decisiones de más de **500,000 productores agropecuarios** colombianos que reportan al sistema EVA anualmente.
