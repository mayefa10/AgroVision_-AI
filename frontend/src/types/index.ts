export type RiskLevel = "low" | "medium" | "high" | "critical";

export interface Region {
  region: string;
  code: string;
  risk: RiskLevel;
  lat: number;
  lng: number;
}

export interface NasaDay {
  fecha: string;
  temperatura: number;
  precipitacion: number;
  humedad: number;
}

export interface EvaRow {
  municipio?: string;
  cultivo?: string;
  area_sembrada?: number;
  area_cosechada?: number;
  produccion?: number;
  rendimiento?: number;
  a_o?: string;
}

export interface PredictionPayload {
  region_code: string;
  prediction_type: string;
  temperatura: number;
  humedad: number;
  precipitacion: number;
  altitud: number;
}

export interface PredictionResult {
  risk: RiskLevel;
  confidence: number;
  prediction_type: string;
  region_code: string;
  message: string;
}

export interface KpiData {
  label: string;
  value: string;
  sub: string;
  color?: string;
  icon: string;
}

export type ClimaTab = "Temperatura" | "Precipitación" | "Humedad";