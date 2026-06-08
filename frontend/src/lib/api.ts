import { AI_URL } from './constants';
import type {
  Region,
  NasaDay,
  EvaRow,
  PredictionPayload,
  PredictionResult,
} from '@/types';

class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) throw new ApiError(res.status, await res.text());
  return res.json();
}

export const api = {
  regions: {
    getRiskSummary: () =>
      fetchJson<{ data: Region[] }>(`${AI_URL}/regions/risk-summary`),
  },

  clima: {
    // CORREGIDO: el endpoint es /clima/{departamento}, no /clima/nasa/{departamento}
    getNasaData: (departamento: string, days = 30) =>
      fetchJson<{ success: boolean; estadisticas: any; data: NasaDay[] }>(
        `${AI_URL}/clima/${encodeURIComponent(departamento)}?days=${days}`,
      ),
  },

  eva: {
    // Pasa departamento, cultivo opcional y limit
    getData: (departamento: string, cultivo?: string, limit = 20) => {
      const params = new URLSearchParams({
        departamento,
        limit: String(limit),
      });
      if (cultivo) params.append('cultivo', cultivo);
      return fetchJson<{
        success:          boolean;
        data:             EvaRow[];
        total_registros:  number;
        estadisticas:     Record<string, number>;
      }>(`${AI_URL}/eva?${params.toString()}`);
    },
  },

  predict: {
    runPrediction: (payload: PredictionPayload) =>
      fetchJson<PredictionResult>(`${AI_URL}/predict-risk`, {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
  },
};