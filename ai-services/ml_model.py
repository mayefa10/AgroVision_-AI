"""
AgroVision AI — Modelo ML Real
Random Forest entrenado con datos EVA (datos.gov.co)

Target: rendimiento (t/ha)
Features: departamento, cultivo, area_sembrada, año, periodo
"""

import httpx
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import pickle
import os
import logging

logger = logging.getLogger(__name__)

MODEL_PATH = "rendimiento_model.pkl"
ENCODERS_PATH = "encoders.pkl"

# ── 1. Fetch datos EVA ────────────────────────────────────

async def fetch_eva_training_data(limit: int = 5000) -> pd.DataFrame:
    """Descarga datos EVA desde datos.gov.co para entrenamiento."""
    url = "https://www.datos.gov.co/resource/uejq-wxrr.json"
    all_data = []

    async with httpx.AsyncClient(timeout=60) as client:
        for offset in range(0, limit, 1000):
            params = {
                "$limit": 1000,
                "$offset": offset,
                "$order": "a_o DESC",
                "$where": "rendimiento IS NOT NULL AND rea_sembrada IS NOT NULL"
            }
            try:
                r = await client.get(url, params=params)
                batch = r.json()
                if not batch:
                    break
                all_data.extend(batch)
            except Exception as e:
                logger.error(f"Error fetching batch at offset {offset}: {e}")
                break

    return pd.DataFrame(all_data)


# ── 2. Preparar features ──────────────────────────────────

def prepare_features(df: pd.DataFrame, encoders: dict = None, fit: bool = True):
    """
    Limpia y prepara el DataFrame para el modelo.
    
    Features:
    - departamento (encoded)
    - cultivo (encoded)  
    - grupo_cultivo (encoded)
    - area_sembrada (numeric)
    - anio (numeric)
    - periodo_num (semestre 1 o 2)
    
    Target:
    - rendimiento (t/ha)
    """
    df = df.copy()

    # Renombrar columnas con caracteres especiales
    rename_map = {
        'c_digo_dane_departamento': 'codigo_dane_dpto',
        'c_digo_dane_municipio': 'codigo_dane_mpio',
        'a_o': 'anio',
        'rea_sembrada': 'area_sembrada',
        'rea_cosechada': 'area_cosechada',
        'producci_n': 'produccion',
        'desagregaci_n_cultivo': 'desagregacion_cultivo',
        'ciclo_del_cultivo': 'ciclo_cultivo',
        'estado_f_sico_del_cultivo': 'estado_fisico',
        'c_digo_del_cultivo': 'codigo_cultivo',
        'nombre_cient_fico_del_cultivo': 'nombre_cientifico',
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    # Convertir numéricos
    for col in ['area_sembrada', 'area_cosechada', 'produccion', 'rendimiento']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    if 'anio' in df.columns:
        df['anio'] = pd.to_numeric(df['anio'], errors='coerce')

    # Periodo → numérico (primer semestre=1, segundo=2, anual=0)
    def parse_periodo(p):
        if pd.isna(p): return 0
        p = str(p).upper()
        if 'PRIMER' in p or '1' in p: return 1
        if 'SEGUNDO' in p or '2' in p: return 2
        return 0

    if 'periodo' in df.columns:
        df['periodo_num'] = df['periodo'].apply(parse_periodo)

    # Eliminar filas sin target
    if 'rendimiento' in df.columns:
        df = df.dropna(subset=['rendimiento'])
        df = df[df['rendimiento'] > 0]
        df = df[df['rendimiento'] < 500]
    

    # Eliminar filas sin features clave
    df = df.dropna(subset=['area_sembrada', 'anio'])
    df = df[df['area_sembrada'] > 0]

    # Encoding categórico
    cat_cols = ['departamento', 'cultivo', 'grupo_cultivo']
    
    if encoders is None:
        encoders = {}

    for col in cat_cols:
        if col not in df.columns:
            df[col] = 'DESCONOCIDO'
        df[col] = df[col].fillna('DESCONOCIDO').str.upper().str.strip()
        
        if fit:
            enc = LabelEncoder()
            df[f'{col}_enc'] = enc.fit_transform(df[col])
            encoders[col] = enc
        else:
            enc = encoders.get(col)
            if enc:
                # Manejar categorías nuevas
                known = set(enc.classes_)
                df[col] = df[col].apply(lambda x: x if x in known else 'DESCONOCIDO')
                if 'DESCONOCIDO' not in enc.classes_:
                    enc.classes_ = np.append(enc.classes_, 'DESCONOCIDO')
                df[f'{col}_enc'] = enc.transform(df[col])
            else:
                df[f'{col}_enc'] = 0

    feature_cols = [
        'departamento_enc', 'cultivo_enc', 'grupo_cultivo_enc',
        'area_sembrada', 'anio', 'periodo_num'
    ]

    # Asegurar que todas las features existen
    for col in feature_cols:
        if col not in df.columns:
            df[col] = 0

    return df[feature_cols], df['rendimiento'], encoders


# ── 3. Entrenar modelo ────────────────────────────────────

async def train_model() -> dict:
    """
    Entrena el modelo Random Forest con datos EVA reales.
    Retorna métricas de evaluación.
    """
    logger.info("Iniciando entrenamiento con datos EVA...")
    
    # Fetch datos
    df = await fetch_eva_training_data(limit=5000)
    
    if df.empty:
        return {"success": False, "message": "No se pudieron obtener datos EVA"}

    logger.info(f"Datos obtenidos: {len(df)} registros")

    # Preparar features
    X, y, encoders = prepare_features(df, fit=True)
    
    logger.info(f"Datos limpios: {len(X)} registros para entrenamiento")

    if len(X) < 100:
        return {"success": False, "message": "Insuficientes datos para entrenar"}

    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Modelo Random Forest
    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=12,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    # Evaluación
    y_pred = model.predict(X_test)
    mae  = mean_absolute_error(y_test, y_pred)
    r2   = r2_score(y_test, y_pred)

    # Feature importance
    feature_names = ['departamento', 'cultivo', 'grupo_cultivo', 'area_sembrada', 'anio', 'periodo']
    importances = dict(zip(feature_names, model.feature_importances_.tolist()))

    # Guardar modelo
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(model, f)
    with open(ENCODERS_PATH, 'wb') as f:
        pickle.dump(encoders, f)

    logger.info(f"Modelo guardado. MAE: {mae:.2f}, R²: {r2:.3f}")

    return {
        "success": True,
        "registros_entrenamiento": len(X_train),
        "registros_test": len(X_test),
        "mae": round(mae, 3),
        "r2": round(r2, 3),
        "feature_importance": importances,
        "model_path": MODEL_PATH,
    }


# ── 4. Predicción ─────────────────────────────────────────

def load_model():
    """Carga el modelo entrenado desde disco."""
    if not os.path.exists(MODEL_PATH):
        return None, None
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
    with open(ENCODERS_PATH, 'rb') as f:
        encoders = pickle.load(f)
    return model, encoders


def predict_rendimiento(
    departamento: str,
    cultivo: str,
    grupo_cultivo: str,
    area_sembrada: float,
    anio: int,
    periodo: int = 0,
) -> dict:
    """
    Predice el rendimiento (t/ha) para un cultivo en una región.
    """
    model, encoders = load_model()

    if model is None:
        return {
            "success": False,
            "message": "Modelo no entrenado. Llama a POST /ml/train primero.",
        }

    # Preparar input
    input_data = pd.DataFrame([{
        'departamento': departamento.upper(),
        'cultivo': cultivo.upper(),
        'grupo_cultivo': grupo_cultivo.upper(),
        'area_sembrada': area_sembrada,
        'anio': anio,
        'periodo_num': periodo,
    }])

    X, _, _ = prepare_features(input_data, encoders=encoders, fit=False)
    prediction = model.predict(X)[0]

    # Clasificar rendimiento
    if prediction > 15:
        nivel = "excelente"
    elif prediction > 8:
        nivel = "bueno"
    elif prediction > 4:
        nivel = "regular"
    else:
        nivel = "bajo"

    return {
        "success": True,
        "departamento": departamento,
        "cultivo": cultivo,
        "rendimiento_predicho": round(float(prediction), 2),
        "unidad": "t/ha",
        "nivel": nivel,
        "anio": anio,
        "area_sembrada": area_sembrada,
    }
