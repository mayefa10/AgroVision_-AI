"use client";
import { useEffect, useState, useCallback } from "react";
import { AI_URL } from "@/lib/constants";

export interface MlMetrics {
  success:                 boolean;
  registros_entrenamiento: number;
  registros_test:          number;
  registros_totales:       number;
  mae:                     number;
  r2:                      number;
  feature_importance:      Record<string, number>;
  model_path:              string;
  trained_at:              string;
}

export function useMlMetrics() {
  const [data, setData]       = useState<MlMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState<string | null>(null);

  const fetchData = useCallback(async (signal: AbortSignal) => {
    setLoading(true);
    setError(null);
    try {
      const r = await fetch(`${AI_URL}/ml/metrics`, { signal });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const json = await r.json();
      if (!json.success) {
        setData(null); // modelo no entrenado todavía — no es un error real
        return;
      }
      setData(json);
    } catch (e: unknown) {
      if ((e as Error).name === "AbortError") return;
      setError((e as Error).message ?? "Error desconocido");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    fetchData(controller.signal);
    return () => controller.abort();
  }, [fetchData]);

  return { data, loading, error };
}