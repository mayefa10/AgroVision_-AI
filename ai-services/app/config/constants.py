"""Constantes globales del proyecto."""

SOCRATA_BASE = "https://www.datos.gov.co/resource"
EVA_2019_2024 = "uejq-wxrr"
NASA_POWER_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
NASA_POWER_ANNUAL_URL = "https://power.larc.nasa.gov/api/temporal/annual/point"
OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5"

DEPARTAMENTOS = {
    "ANTIOQUIA":       {"lat": 6.2442,  "lng": -75.5812, "capital": "Medellin",      "codigo": "05"},
    "ATLANTICO":       {"lat": 10.9639, "lng": -74.7964, "capital": "Barranquilla",  "codigo": "08"},
    "BOLIVAR":         {"lat": 8.6706,  "lng": -74.0328, "capital": "Cartagena",     "codigo": "13"},
    "BOYACA":          {"lat": 5.5353,  "lng": -73.3678, "capital": "Tunja",         "codigo": "15"},
    "CALDAS":          {"lat": 5.0689,  "lng": -75.5174, "capital": "Manizales",     "codigo": "17"},
    "CAUCA":           {"lat": 2.4448,  "lng": -76.6147, "capital": "Popayan",       "codigo": "19"},
    "CESAR":           {"lat": 10.4631, "lng": -73.2532, "capital": "Valledupar",    "codigo": "20"},
    "CORDOBA":         {"lat": 8.7479,  "lng": -75.8814, "capital": "Monteria",      "codigo": "23"},
    "CUNDINAMARCA":    {"lat": 4.7110,  "lng": -74.0721, "capital": "Bogota",        "codigo": "25"},
    "HUILA":           {"lat": 2.9273,  "lng": -75.2819, "capital": "Neiva",         "codigo": "41"},
    "GUAJIRA":         {"lat": 11.5444, "lng": -72.9072, "capital": "Riohacha",      "codigo": "44"},
    "MAGDALENA":       {"lat": 10.4195, "lng": -74.4061, "capital": "Santa Marta",   "codigo": "47"},
    "META":            {"lat": 4.1420,  "lng": -73.6266, "capital": "Villavicencio", "codigo": "50"},
    "NARINO":          {"lat": 1.2136,  "lng": -77.2811, "capital": "Pasto",         "codigo": "52"},
    "NORTE DE SANTANDER": {"lat": 7.8939, "lng": -72.5078, "capital": "Cucuta",     "codigo": "54"},
    "SANTANDER":       {"lat": 7.1193,  "lng": -73.1227, "capital": "Bucaramanga",  "codigo": "68"},
    "TOLIMA":          {"lat": 4.4389,  "lng": -75.2322, "capital": "Ibague",        "codigo": "73"},
    "VALLE DEL CAUCA": {"lat": 3.4516,  "lng": -76.5320, "capital": "Cali",          "codigo": "76"},
}

ENSO_HISTORICO = {
    2007: {"fase": "La Nina",  "intensidad": "moderada", "oni": -1.2},
    2008: {"fase": "La Nina",  "intensidad": "moderada", "oni": -0.8},
    2009: {"fase": "El Nino",  "intensidad": "moderada", "oni": 0.9},
    2010: {"fase": "La Nina",  "intensidad": "fuerte",   "oni": -1.5},
    2011: {"fase": "La Nina",  "intensidad": "moderada", "oni": -1.0},
    2012: {"fase": "Neutro",   "intensidad": "neutro",   "oni": 0.2},
    2013: {"fase": "Neutro",   "intensidad": "neutro",   "oni": 0.1},
    2014: {"fase": "El Nino",  "intensidad": "debil",    "oni": 0.6},
    2015: {"fase": "El Nino",  "intensidad": "fuerte",   "oni": 2.3},
    2016: {"fase": "La Nina",  "intensidad": "debil",    "oni": -0.7},
    2017: {"fase": "La Nina",  "intensidad": "debil",    "oni": -0.8},
    2018: {"fase": "El Nino",  "intensidad": "debil",    "oni": 0.8},
    2019: {"fase": "El Nino",  "intensidad": "debil",    "oni": 0.5},
    2020: {"fase": "La Nina",  "intensidad": "moderada", "oni": -1.2},
    2021: {"fase": "La Nina",  "intensidad": "moderada", "oni": -1.0},
    2022: {"fase": "La Nina",  "intensidad": "moderada", "oni": -0.9},
    2023: {"fase": "El Nino",  "intensidad": "fuerte",   "oni": 2.0},
    2024: {"fase": "La Nina",  "intensidad": "debil",    "oni": -0.6},
    2025: {"fase": "Neutro",   "intensidad": "neutro",   "oni": 0.1},
    2026: {"fase": "La Nina",  "intensidad": "debil",    "oni": -0.6},
}

UMBRALES_ALERTAS = {
    "sequia":        {"precipitacion_min": 5, "humedad_min": 40, "temperatura_max": 32, "dias_sin_lluvia": 7},
    "inundacion":    {"precipitacion_max": 60, "humedad_max": 88},
    "helada":        {"temperatura_min": 8},
    "estres_termico":{"temperatura_max": 35, "humedad_min": 30},
}

CULTIVOS_VULNERABLES = {
    "sequia":         ["MAIZ", "FRIJOL", "ARROZ", "PAPA", "SORGO"],
    "inundacion":     ["ARROZ", "MAIZ", "PAPA", "CEBOLLA"],
    "helada":         ["PAPA", "FRIJOL", "ARVEJA", "TRIGO", "CEBADA"],
    "estres_termico": ["PAPA", "FRIJOL", "TOMATE", "ARVEJA"],
}