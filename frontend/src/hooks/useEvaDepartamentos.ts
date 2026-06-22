"use client";
import { useEffect, useState, useCallback } from "react";
import { AI_URL } from "@/lib/constants";

export interface EvaDepartamento {
  nombre:           string;
  total_registros:  number;
}

export function useEvaDepartamentos() {
  const [departamentos, setDepartamentos] = useState<string[]>([]);
  const [loading, setLoading]             = useState(true);
  const [error, setError]                 = useState<string | null>(null);

  const fetchData = useCallback(async (signal: AbortSignal) => {
    setLoading(true);
    setError(null);
    try {
      const r = await fetch(`${AI_URL}/eva/departamentos`, { signal });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const json = await r.json();

      if (!json.success) throw new Error(json.message ?? "Sin datos");

      // Extraer solo los nombres ordenados
      const nombres: string[] = (json.departamentos as EvaDepartamento[])
        .filter((d) => d.total_registros > 0)
        .map((d) => d.nombre.toUpperCase());

      setDepartamentos(nombres);
    } catch (e: unknown) {
      if ((e as Error).name === "AbortError") return;
      // Si falla, usar lista de respaldo para no dejar el selector vacío
      setError((e as Error).message);
      setDepartamentos(FALLBACK_DEPARTAMENTOS);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    fetchData(controller.signal);
    return () => controller.abort();
  }, [fetchData]);

  return { departamentos, loading, error };
}

// Lista de respaldo en caso de que la API no responda
const FALLBACK_DEPARTAMENTOS = [
  "ANTIOQUIA", "BOLIVAR", "BOYACA", "CALDAS", "CAUCA",
  "CESAR", "CORDOBA", "CUNDINAMARCA", "HUILA", "MAGDALENA",
  "META", "NARINO", "NORTE DE SANTANDER", "SANTANDER",
  "TOLIMA", "VALLE DEL CAUCA",
];