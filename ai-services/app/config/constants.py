"""
AgroVision AI — Constantes globales.
Fuente única de verdad para datos geográficos, umbrales y endpoints.
"""
from __future__ import annotations

# ── URLs y datasets ───────────────────────────────────────

SOCRATA_BASE     = "https://www.datos.gov.co/resource"
NASA_DAILY_URL   = "https://power.larc.nasa.gov/api/temporal/daily/point"
NASA_ANNUAL_URL  = "https://power.larc.nasa.gov/api/temporal/annual/point"
OPENWEATHER_URL  = "https://api.openweathermap.org/data/2.5"

EVA_2019_2024    = "uejq-wxrr"
EVA_HISTORICO    = "2pnw-mmge"
DIVIPOLA_GEO     = "vafm-j2df"
DIVIPOLA_CODIGOS = "gdxc-w37w"

# ── Departamentos ─────────────────────────────────────────

DEPARTAMENTOS: dict[str, dict] = {
    "ANTIOQUIA":          {"lat": 6.2442,  "lng": -75.5812, "capital": "Medellin",      "codigo": "05"},
    "ATLANTICO":          {"lat": 10.9639, "lng": -74.7964, "capital": "Barranquilla",  "codigo": "08"},
    "BOLIVAR":            {"lat": 8.6706,  "lng": -74.0328, "capital": "Cartagena",     "codigo": "13"},
    "BOYACA":             {"lat": 5.5353,  "lng": -73.3678, "capital": "Tunja",         "codigo": "15"},
    "CALDAS":             {"lat": 5.0689,  "lng": -75.5174, "capital": "Manizales",     "codigo": "17"},
    "CAQUETA":            {"lat": 1.6144,  "lng": -75.6062, "capital": "Florencia",     "codigo": "18"},
    "CAUCA":              {"lat": 2.4448,  "lng": -76.6147, "capital": "Popayan",       "codigo": "19"},
    "CESAR":              {"lat": 10.4631, "lng": -73.2532, "capital": "Valledupar",    "codigo": "20"},
    "CHOCO":              {"lat": 5.6920,  "lng": -76.6583, "capital": "Quibdo",        "codigo": "27"},
    "CORDOBA":            {"lat": 8.7479,  "lng": -75.8814, "capital": "Monteria",      "codigo": "23"},
    "CUNDINAMARCA":       {"lat": 4.7110,  "lng": -74.0721, "capital": "Bogota",        "codigo": "25"},
    "GUAJIRA":            {"lat": 11.5444, "lng": -72.9072, "capital": "Riohacha",      "codigo": "44"},
    "HUILA":              {"lat": 2.9273,  "lng": -75.2819, "capital": "Neiva",         "codigo": "41"},
    "MAGDALENA":          {"lat": 11.2408, "lng": -74.1990, "capital": "Santa Marta",   "codigo": "47"},
    "META":               {"lat": 4.1420,  "lng": -73.6266, "capital": "Villavicencio", "codigo": "50"},
    "NARINO":             {"lat": 1.2136,  "lng": -77.2811, "capital": "Pasto",         "codigo": "52"},
    "NORTE DE SANTANDER": {"lat": 7.8939,  "lng": -72.5078, "capital": "Cucuta",        "codigo": "54"},
    "SANTANDER":          {"lat": 7.1193,  "lng": -73.1227, "capital": "Bucaramanga",   "codigo": "68"},
    "SUCRE":              {"lat": 9.3047,  "lng": -75.3978, "capital": "Sincelejo",     "codigo": "70"},
    "TOLIMA":             {"lat": 4.4389,  "lng": -75.2322, "capital": "Ibague",        "codigo": "73"},
    "VALLE DEL CAUCA":    {"lat": 3.4516,  "lng": -76.5320, "capital": "Cali",          "codigo": "76"},
}

# ── Cultivos por departamento ─────────────────────────────

CULTIVOS_DEPTO: dict[str, list[str]] = {
    "ANTIOQUIA":       ["CAFE", "MAIZ", "AGUACATE", "PAPA"],
    "CUNDINAMARCA":    ["PAPA", "MAIZ", "FRIJOL", "ARROZ"],
    "VALLE DEL CAUCA": ["CANA DE AZUCAR", "MAIZ", "SOYA"],
    "TOLIMA":          ["ARROZ", "MAIZ", "SORGO", "CAFE"],
    "META":            ["ARROZ", "MAIZ", "PALMA", "SOYA"],
    "BOYACA":          ["PAPA", "MAIZ", "FRIJOL", "CEBOLLA"],
    "CORDOBA":         ["MAIZ", "ARROZ", "NAME", "YUCA"],
    "NARINO":          ["PAPA", "MAIZ", "CAFE", "FRIJOL"],
    "SANTANDER":       ["CAFE", "MAIZ", "CACAO", "ARROZ"],
    "HUILA":           ["CAFE", "ARROZ", "MAIZ", "SORGO"],
}

# ── Cultivos vulnerables por tipo de alerta ───────────────

CULTIVOS_VULNERABLES: dict[str, list[str]] = {
    "sequia":         ["MAIZ", "FRIJOL", "ARROZ", "PAPA", "SORGO"],
    "inundacion":     ["ARROZ", "MAIZ", "PAPA", "CEBOLLA"],
    "helada":         ["PAPA", "FRIJOL", "ARVEJA", "TRIGO", "CEBADA"],
    "estres_termico": ["PAPA", "FRIJOL", "TOMATE", "ARVEJA"],
}

# ── Umbrales agronómicos ──────────────────────────────────

UMBRALES: dict[str, dict] = {
    "sequia": {
        "precipitacion_min":  5,    # mm/día
        "humedad_min":        40,   # %
        "temperatura_max":    32,   # °C
        "dias_sin_lluvia":    7,
    },
    "inundacion": {
        "precipitacion_max":  60,   # mm/día
        "humedad_max":        88,   # %
        "precipitacion_alta": 40,
    },
    "helada": {
        "temperatura_min": 8,       # °C
        "critica":         2,
        "alta":            5,
    },
    "estres_termico": {
        "temperatura_max": 35,      # °C
        "humedad_min":     30,      # %
    },
}

# ── ENSO histórico (índice ONI) ───────────────────────────

ENSO_HISTORICO: dict[int, dict] = {
    2007: {"fase": "La Nina",  "intensidad": "moderada", "oni": -1.2},
    2008: {"fase": "La Nina",  "intensidad": "moderada", "oni": -0.8},
    2009: {"fase": "El Nino",  "intensidad": "moderada", "oni":  0.9},
    2010: {"fase": "La Nina",  "intensidad": "fuerte",   "oni": -1.5},
    2011: {"fase": "La Nina",  "intensidad": "moderada", "oni": -1.0},
    2012: {"fase": "Neutro",   "intensidad": "neutro",   "oni":  0.2},
    2013: {"fase": "Neutro",   "intensidad": "neutro",   "oni":  0.1},
    2014: {"fase": "El Nino",  "intensidad": "debil",    "oni":  0.6},
    2015: {"fase": "El Nino",  "intensidad": "fuerte",   "oni":  2.3},
    2016: {"fase": "La Nina",  "intensidad": "debil",    "oni": -0.7},
    2017: {"fase": "La Nina",  "intensidad": "debil",    "oni": -0.8},
    2018: {"fase": "El Nino",  "intensidad": "debil",    "oni":  0.8},
    2019: {"fase": "El Nino",  "intensidad": "debil",    "oni":  0.5},
    2020: {"fase": "La Nina",  "intensidad": "moderada", "oni": -1.2},
    2021: {"fase": "La Nina",  "intensidad": "moderada", "oni": -1.0},
    2022: {"fase": "La Nina",  "intensidad": "moderada", "oni": -0.9},
    2023: {"fase": "El Nino",  "intensidad": "fuerte",   "oni":  2.0},
    2024: {"fase": "La Nina",  "intensidad": "debil",    "oni": -0.6},
}

# ── Rutas de almacenamiento ───────────────────────────────

DATASETS_PATH   = "/app/datasets"
RAW_PATH        = f"{DATASETS_PATH}/raw"
PROCESSED_PATH  = f"{DATASETS_PATH}/processed"
FEATURES_PATH   = f"{DATASETS_PATH}/features"
CLEANED_PATH    = f"{DATASETS_PATH}/cleaned"
REPORTS_PATH    = f"{DATASETS_PATH}/reports"
MODEL_PATH      = "/app/models/rendimiento_model.pkl"
ENCODERS_PATH   = "/app/models/encoders.pkl"
METRICS_PATH    = "/app/models/metrics.json"
CLEANING_ENCODERS_PATH = "/app/models/cleaning_encoders.json"

# ── Dataset catálogo datos.gov.co ─────────────────────────

CATALOGO_DATASET_ID = "uzcf-b9dh"   # Portal Nacional - SODA2
CATALOGO_URL        = f"{SOCRATA_BASE}/{CATALOGO_DATASET_ID}.json"

# ── Configuración limpieza de datos ──────────────────────

LIMPIEZA: dict[str, object] = {
    # Umbral de nulos por columna: si supera este % → eliminar columna
    "umbral_nulos_cols":  0.60,
    # Umbral de nulos por fila: si supera este % → eliminar fila
    "umbral_nulos_filas": 0.70,
    # IQR multiplicador para outliers
    "iqr_mult": 1.5,
    # Z-score umbral para outliers
    "zscore_umbral": 3.0,
    # Cardinalidad máxima para One-Hot (si supera → Label Encoding)
    "max_cardinalidad_onehot": 10,
    # Columnas que siempre se eliminan (IDs, URLs, metadatos de sistema)
    "cols_siempre_eliminar": [
        "url", "api_endpoint", "uid", "owner_uid",
        "parent_uid", "contact_email", "attribution_link", "row_label",
    ],
    # Columnas de fecha a convertir y expandir en features
    "cols_fecha": [
        "creation_date",
        "last_metadata_updated_date",
        "last_data_updated_date",
        "informacindedatos_fechaemisinaaaammdd",
        "informacindedatos_fechaemisinddmmaaaa",
    ],
    # Columnas numéricas almacenadas como string
    "cols_numericas_string": [
        "visits", "downloads", "column_count", "row_count",
    ],
}