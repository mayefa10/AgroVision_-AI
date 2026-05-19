"use client"
import type { RiskLevel, NasaDay, ClimaTab } from "@/types";

export const AI_URL = process.env.NEXT_PUBLIC_AI_SERVICE_URL || "http://localhost:8000";

export const RISK_COLORS: Record<RiskLevel, string> = {
  low: "#22c55e",
  medium: "#f59e0b",
  high: "#f97316",
  critical: "#ef4444",
};

export const RISK_BG: Record<RiskLevel, string> = {
  low: "#dcfce7",
  medium: "#fef3c7",
  high: "#ffedd5",
  critical: "#fee2e2",
};

export const RISK_LABELS: Record<RiskLevel, string> = {
  low: "Bajo",
  medium: "Medio",
  high: "Alto",
  critical: "Crítico",
};

export const NAV_ITEMS = [
  { id: "overview", label: "Resumen", icon: "◈" },
  { id: "clima", label: "Clima", icon: "◉" },
  { id: "agricola", label: "Agrícola", icon: "◐" },
  { id: "prediccion", label: "Predicción", icon: "◑" },
] as const;

export const DEPARTMENTS = [
  "ANTIOQUIA",
  "CUNDINAMARCA",
  "VALLE DEL CAUCA",
  "TOLIMA",
  "SANTANDER",
  "META",
] as const;

export const CLIMA_TABS: ClimaTab[] = ["Temperatura", "Precipitación", "Humedad"];

export const CLIMA_KEY: Record<ClimaTab, keyof NasaDay> = {
  Temperatura: "temperatura",
  Precipitación: "precipitacion",
  Humedad: "humedad",
};