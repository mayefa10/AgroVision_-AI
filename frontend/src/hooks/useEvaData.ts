"use client";
import { useState, useEffect } from "react";
import { api } from "@/lib/api";
import type { EvaRow } from "@/types";

export function useEvaData(departamento = "ANTIOQUIA") {
  const [data, setData] = useState<EvaRow[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    api.eva.getData(departamento)
      .then((res) => {
        if (mounted) {
          // La API retorna { success, data, total_registros }
          const rows = res.data || [];
          setData(rows.slice(0, 15));
        }
      })
      .catch(() => {})
      .finally(() => { if (mounted) setLoading(false); });
    return () => { mounted = false; };
  }, [departamento]);

  return { data, loading };
}