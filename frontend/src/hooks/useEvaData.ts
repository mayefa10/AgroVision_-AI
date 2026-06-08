"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api";
import type { EvaRow } from "@/types";

const PAGE_SIZE = 15;

/**
 * Hook para obtener datos EVA del backend.
 *
 * @param departamento  Nombre del departamento en mayúsculas (default: "ANTIOQUIA")
 * @param cultivo       Nombre del cultivo en mayúsculas (undefined = todos)
 * @param limit         Máximo de registros a mostrar (default: 15)
 */
export function useEvaData(
  departamento = "ANTIOQUIA",
  cultivo?: string,
  limit = PAGE_SIZE,
) {
  const [data, setData]                   = useState<EvaRow[]>([]);
  const [loading, setLoading]             = useState(true);
  const [error, setError]                 = useState<string | null>(null);
  const [totalRegistros, setTotalRegistros] = useState<number | null>(null);

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    setError(null);

    api.eva
      .getData(departamento, cultivo)          // pasa cultivo al endpoint
      .then((res) => {
        if (!mounted) return;
        const rows: EvaRow[] = res.data ?? [];
        setData(rows.slice(0, limit));
        // El backend retorna total_registros en la respuesta
        setTotalRegistros(res.total_registros ?? rows.length);
      })
      .catch((err) => {
        if (!mounted) return;
        setError(err?.message ?? "Error al cargar datos EVA");
        setData([]);
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });

    return () => {
      mounted = false;
    };
  // Se re-ejecuta cuando cambia departamento O cultivo
  }, [departamento, cultivo, limit]);

  return { data, loading, error, totalRegistros };
}