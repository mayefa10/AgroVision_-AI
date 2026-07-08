# Diccionario de datos — AgroVision AI

## Dataset consolidado: EVA + Clima + ENSO

Total variables en el modelo ML: **12 variables**

### Variables de producción agrícola (EVA — datos.gov.co)

| Variable | Tipo | Descripción | Rango válido | Fuente |
|----------|------|-------------|--------------|--------|
| `departamento` | Categórica | Nombre del departamento colombiano | 32 valores únicos | EVA |
| `municipio` | Categórica | Nombre del municipio | ~1,100 valores | EVA |
| `cultivo` | Categórica | Nombre del cultivo evaluado | ~80 cultivos | EVA |
| `grupo_cultivo` | Categórica | Categoría del cultivo | Cereales, Frutas, etc. | EVA |
| `area_sembrada` | Numérica (ha) | Hectáreas sembradas | > 0 | EVA |
| `area_cosechada` | Numérica (ha) | Hectáreas cosechadas | ≥ 0 | EVA |
| `produccion` | Numérica (t) | Toneladas producidas | ≥ 0 (puede ser null 2024) | EVA |
| `rendimiento` | Numérica (t/ha) | Producción / área cosechada | 0 < r < 50 | EVA |
| `anio` | Entero | Año de la evaluación | 2019-2024 | EVA |
| `periodo_num` | Entero | Semestre (0, 1, 2) | {0, 1, 2} | EVA |

### Variables derivadas (feature engineering)

| Variable | Tipo | Descripción | Cálculo |
|----------|------|-------------|---------|
| `departamento_enc` | Entero | Departamento codificado | LabelEncoder |
| `municipio_enc` | Entero | Municipio codificado | LabelEncoder |
| `cultivo_enc` | Entero | Cultivo codificado | LabelEncoder |
| `grupo_cultivo_enc` | Entero | Grupo de cultivo codificado | LabelEncoder |
| `ratio_cosecha` | Decimal [0,1] | Eficiencia productiva | `area_cosechada / area_sembrada` |
| `rendimiento_hist_prom` | Numérica (t/ha) | Baseline histórico | Media por depto+cultivo |

### Variables climáticas (NOAA/CPC)

| Variable | Tipo | Descripción | Rango |
|----------|------|-------------|-------|
| `oni_index` | Decimal | Índice Oceánico Niño | -3.0 a +3.0 |
| `riesgo_climatico_enc` | Entero [0-4] | Categoría ENSO codificada | 0=La Niña fuerte, 4=El Niño fuerte |

### Variables climáticas en tiempo real (NASA POWER / OpenWeather)

| Variable | Tipo | Unidad | Descripción |
|----------|------|--------|-------------|
| `temperatura` | Decimal | °C | Temperatura a 2m de altura |
| `precipitacion` | Decimal | mm/día | Precipitación diaria corregida |
| `humedad` | Decimal | % | Humedad relativa a 2m |
| `radiacion_solar` | Decimal | MJ/m² | Radiación solar en superficie |
| `viento` | Decimal | m/s | Velocidad del viento a 2m |

## Tratamiento de valores nulos

| Campo | Tratamiento | Justificación |
|-------|-------------|---------------|
| `area_sembrada` null | Excluir del entrenamiento | Sin área no hay rendimiento válido |
| `area_cosechada` null | Imputar con `area_sembrada` | Proxy conservador |
| `produccion` null (2024) | Mostrar "—" en UI | Datos aún no reportados en la fuente |
| `rendimiento` null | Excluir del entrenamiento | Variable target, no puede imputarse |
| Duplicados | Deduplicar por municipio+cultivo+año+periodo | Evitar sesgo por reportes dobles |

## Codificación ENSO

| Valor `oni_index` | Categoría | `riesgo_climatico_enc` |
|------------------|-----------|----------------------|
| ≤ -1.5 | La Niña fuerte | 0 |
| -1.5 a -0.5 | La Niña | 1 |
| -0.5 a +0.5 | Neutro | 2 |
| +0.5 a +1.5 | El Niño | 3 |
| ≥ +1.5 | El Niño fuerte | 4 |
