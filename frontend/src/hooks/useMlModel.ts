"use client";
import { useState } from "react";
import { AI_URL } from "@/lib/constants";

export interface MlResult {
  success: boolean;
  departamento: string;
  cultivo: string;
  rendimiento_predicho: number;
  unidad: string;
  nivel: string;
  anio: number;
  area_sembrada: number;
}

export interface TrainResult {
  success: boolean;
  registros_entrenamiento: number;
  registros_test: number;
  mae: number;
  r2: number;
  feature_importance: Record<string, number>;
}

export function useMlModel() {
  const [result, setResult] = useState<MlResult | null>(null);
  const [trainResult, setTrainResult] = useState<TrainResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [training, setTraining] = useState(false);

  async function predict(payload: {
    departamento: string;
    cultivo: string;
    grupo_cultivo: string;
    area_sembrada: number;
    anio: number;
    periodo: number;
  }) {
    setLoading(true);
    try {
      const r = await fetch(`${AI_URL}/ml/predict-rendimiento`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await r.json();
      setResult(data);
      return data;
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }

  async function train() {
    setTraining(true);
    try {
      const r = await fetch(`${AI_URL}/ml/train`, { method: "POST" });
      const data = await r.json();
      setTrainResult(data);
      return data;
    } catch (e) {
      console.error(e);
    } finally {
      setTraining(false);
    }
  }

  return { result, trainResult, loading, training, predict, train };
}
