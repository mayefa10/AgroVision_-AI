"use client";
import { useState, useCallback } from "react";
import { api } from "@/lib/api";
import type { PredictionPayload, PredictionResult } from "@/types";

const DEFAULT_PAYLOAD: PredictionPayload = {
  region_code: "05001",
  prediction_type: "sequia",
  temperatura: 31,
  humedad: 42,
  precipitacion: 4.5,
  altitud: 800,
};

export function usePrediction() {
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const execute = useCallback(async (payload = DEFAULT_PAYLOAD) => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.predict.runPrediction(payload);
      setResult(data);
      return data;
    } catch (e) {
      setError(e as Error);
      throw e;
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setResult(null);
    setError(null);
  }, []);

  return { result, loading, error, execute, reset };
}