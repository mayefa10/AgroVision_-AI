# Changelog — AgroVision AI

Registro cronológico de versiones y cambios.

## [2.0.0] — 2026-07-08

### Agregado
- Cache PostgreSQL para EVA, NASA POWER y OpenWeather (patrón cache-aside con TTL)
- Modelo ML ampliado a 12 features (de 6 a 12 variables)
- Endpoint dinámico `GET /eva/departamentos` con datos reales
- Tarjeta de métricas ML en dashboard (MAE, R², feature importance)
- Volumen Docker persistente para modelo entrenado (`./models`)
- Deduplicación de datos EVA por municipio+cultivo+año+periodo
- Notebooks de análisis exploratorio y modelado
- Documentación técnica completa en `docs/`

### Mejorado
- MAE mejoró de ±3.6 a ±2.93 t/ha (+19%)
- R² mejoró de 0.577 a 0.697 (+21%)
- Registros de entrenamiento: de 4,647 a 12,177 únicos
- Routers FastAPI registrados correctamente (eliminados warnings Operation ID duplicado)

## [1.5.0] — 2026-06-25

### Agregado
- Sección OpenWeather (clima actual por capital departamental)
- Monitor ENSO con datos reales NOAA/CPC
- Escenarios IA (El Niño / La Niña) con impacto por cultivo
- Cache PostgreSQL inicial para EVA

### Mejorado
- Selectores dinámicos reemplazan listas estáticas
- Manejo correcto de nulos: "—" en vez de "0 ha"

## [1.0.0] — 2026-05-29

### Agregado
- Dashboard con 8 secciones: Clima, EVA, Alertas, Mapa, Predicción, ENSO, OpenWeather, Escenarios
- Modelo ML Random Forest con 6 features (R²: 0.577)
- Integración NASA POWER para datos climáticos
- Integración EVA datos.gov.co
- Sistema de alertas agroclimáticas automáticas
- Arquitectura Docker Compose con 5 contenedores
- Backend NestJS con autenticación JWT
- Landing page responsive
