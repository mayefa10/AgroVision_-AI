"use client";
import { useEffect, useState, useCallback } from "react";
import { AI_URL } from "@/lib/constants";

export interface WeatherCondiciones {
  temperatura:       number;
  sensacion_termica: number;
  temperatura_max:   number;
  temperatura_min:   number;
  humedad:           number;
  presion:           number;
  descripcion:       string;
  nubosidad:         number;
  viento_velocidad:  number;
  visibilidad:       number;
}

export interface WeatherData {
  success:      boolean;
  ciudad:       string;
  departamento: string;
  condiciones:  WeatherCondiciones;
  coordenadas:  { lat: number; lng: number };
  fetched_at:   string;
}

export function useOpenWeather(departamento: string) {
  const [data, setData]       = useState<WeatherData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState<string | null>(null);

  const fetchData = useCallback(async (signal: AbortSignal) => {
    if (!departamento) return;
    setLoading(true);
    setError(null);
    try {
      const r = await fetch(
        `${AI_URL}/openweather/${encodeURIComponent(departamento)}`,
        { signal }
      );
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const json = await r.json();
      if (!json.success) throw new Error(json.message ?? "Sin datos");
      setData(json);
    } catch (e: unknown) {
      if ((e as Error).name === "AbortError") return;
      setError((e as Error).message ?? "Error desconocido");
    } finally {
      setLoading(false);
    }
  }, [departamento]);

  useEffect(() => {
    const controller = new AbortController();
    fetchData(controller.signal);
    return () => controller.abort();
  }, [fetchData]);

  return { data, loading, error };
}