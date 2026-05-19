"use client";
import { useState, useEffect } from "react";
import { api } from "@/lib/api";
import type { Region } from "@/types";

export function useRegions() {
  const [regions, setRegions] = useState<Region[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let mounted = true;
    api.regions.getRiskSummary()
      .then(({ data }) => { if (mounted) setRegions(data); })
      .catch((e) => { if (mounted) setError(e); })
      .finally(() => { if (mounted) setLoading(false); });
    return () => { mounted = false; };
  }, []);

  const riskCounts = {
    critical: regions.filter((r) => r.risk === "critical").length,
    high: regions.filter((r) => r.risk === "high").length,
    medium: regions.filter((r) => r.risk === "medium").length,
    low: regions.filter((r) => r.risk === "low").length,
  };

  return { regions, riskCounts, loading, error };
}