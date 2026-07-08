# Fuentes de datos — AgroVision AI

## 1. EVA — Evaluaciones Agropecuarias (datos.gov.co)

| Campo | Valor |
|-------|-------|
| Proveedor | UPRA / Ministerio de Agricultura y Desarrollo Rural |
| URL | https://www.datos.gov.co/Agricultura-y-Desarrollo-Rural/Evaluaciones-Agropecuarias-Municipales-EVA/2pnb-mvck |
| Dataset ID | `uejq-wxrr` |
| API Endpoint | `https://www.datos.gov.co/resource/uejq-wxrr.json` |
| Registros | 145,000+ |
| Cobertura | 32 departamentos · 2019-2024 |
| Actualización | Anual (cierre de campaña agrícola) |
| Licencia | Datos abiertos Colombia |

**Variables principales**: municipio, departamento, cultivo, grupo_cultivo, area_sembrada, area_cosechada, produccion, rendimiento, anio, periodo

---

## 2. NASA POWER — Parámetros Climatológicos

| Campo | Valor |
|-------|-------|
| Proveedor | NASA / Langley Research Center (LaRC) |
| URL | https://power.larc.nasa.gov/ |
| API Endpoint | `https://power.larc.nasa.gov/api/temporal/daily/point` |
| Cobertura | Nacional (por coordenadas) |
| Resolución | Diaria |
| Licencia | Datos públicos NASA |

**Variables**: T2M (temperatura), PRECTOTCORR (precipitación), RH2M (humedad), ALLSKY_SFC_SW_DWN (radiación), WS2M (viento)

---

## 3. NOAA/CPC — Oceanic Niño Index (ONI)

| Campo | Valor |
|-------|-------|
| Proveedor | NOAA / Climate Prediction Center |
| URL | https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt |
| Formato | Texto plano (no JSON) |
| Actualización | Mensual (datos trimestrales) |
| Licencia | Datos públicos NOAA |

**Variables**: season (trimestre), year (año), ONI (índice), fase ENSO

---

## 4. OpenWeather — Clima actual

| Campo | Valor |
|-------|-------|
| Proveedor | OpenWeatherMap |
| URL | https://openweathermap.org/api |
| API Endpoint | `https://api.openweathermap.org/data/2.5/weather` |
| Actualización | Tiempo real |
| Licencia | Free tier (API key requerida) |

**Variables**: temperatura, sensación térmica, humedad, presión, viento, nubosidad, visibilidad

---

## 5. DANE DIVIPOLA — División Político-Administrativa

| Campo | Valor |
|-------|-------|
| Proveedor | DANE Colombia |
| URL | https://www.datos.gov.co/Mapas-Nacionales/DIVIPOLA/gdxc-w37w |
| Dataset ID | `gdxc-w37w` |
| API Endpoint | `https://www.datos.gov.co/resource/gdxc-w37w.json` |
| Cobertura | Nacional |
| Licencia | Datos abiertos Colombia |

**Variables**: codigo_dane, nombre_municipio, nombre_departamento, latitud, longitud

---

## Cumplimiento de requisitos del concurso

- Total fuentes: **5** (rango requerido: 3-10) ✅
- Fuentes de datos.gov.co: **2** (EVA + DANE) ✅
- Al menos 1 de datos.gov.co: **cumplido** ✅
