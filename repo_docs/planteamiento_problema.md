# Planteamiento del problema

## Contexto

Colombia es uno de los países con mayor diversidad agrícola de América Latina, con más de 200 cultivos registrados en el sistema EVA (Evaluaciones Agropecuarias) del Ministerio de Agricultura. Sin embargo, el sector enfrenta una paradoja: existen más de **145,000 registros de evaluaciones agropecuarias** disponibles públicamente en datos.gov.co, pero los productores rurales y las entidades territoriales no cuentan con herramientas que transformen esos datos en decisiones accionables.

## Problema identificado

Los productores agrícolas y las entidades de planificación territorial en Colombia enfrentan tres brechas críticas:

### 1. Información fragmentada
Los datos climáticos (NASA POWER, NOAA), los datos de producción (EVA/UPRA), la información geográfica (DANE) y el clima actual (OpenWeather) existen en silos separados, sin integración que permita análisis cruzados.

### 2. Ausencia de predicción de riesgos agroclimáticos
No existen herramientas públicas que conecten el fenómeno ENSO (El Niño / La Niña) con impactos específicos sobre cultivos por departamento. Los agricultores reciben alertas genéricas sin contexto local.

### 3. Alertas tardías
Las alertas climáticas llegan después de que el daño ocurrió. Se necesita un sistema proactivo basado en datos satelitales y modelos predictivos.

## Pregunta de investigación

> ¿Es posible construir un sistema de inteligencia artificial que integre datos abiertos de múltiples fuentes para predecir el rendimiento agrícola y generar alertas tempranas de riesgo agroclimático en Colombia?

## Población objetivo

- **Primaria**: Productores agrícolas y técnicos agropecuarios de los 32 departamentos de Colombia
- **Secundaria**: Secretarías de Agricultura departamentales, UPRA, Ministerio de Agricultura
- **Terciaria**: Investigadores y analistas de seguridad alimentaria

## Alcance

- Cobertura: 32 departamentos de Colombia
- Período histórico: 2019-2024 (datos EVA)
- Variables climáticas: Temperatura, precipitación, humedad, radiación solar (NASA POWER)
- Fenómeno ENSO: Índice ONI tiempo real (NOAA/CPC)
- Cultivos cubiertos: ~80 cultivos registrados en EVA
