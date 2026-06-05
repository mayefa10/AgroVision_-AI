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
    getNasaData: (region: string, days = 30) =>
      fetchJson<{ data: NasaDay[]; estadisticas: any }>(
        `${AI_URL}/clima/nasa/${region}?days=${days}`,
      ),
  },
  eva: {
    getData: (departamento: string, cultivo?: string, limit = 20) =>
      fetchJson<{
        success: boolean;
        data: EvaRow[];
        total_registros: number;
      }>(
        `${AI_URL}/eva?departamento=${encodeURIComponent(
          departamento,
        )}&limit=${limit}${
          cultivo ? `&cultivo=${encodeURIComponent(cultivo)}` : ''
        }`,
      ),
  },
  predict: {
    runPrediction: (payload: PredictionPayload) =>
      fetchJson<PredictionResult>(`${AI_URL}/predict-risk`, {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
  },
};
