"use client";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import type { NasaDay, ClimaTab } from "@/types";

interface Props {
  data: NasaDay[];
  dataKey: keyof NasaDay;
  tab: ClimaTab;
}

const UNITS: Record<ClimaTab, string> = {
  Temperatura: "°C",
  Precipitación: "mm",
  Humedad: "%",
};

export function ClimateAreaChart({ data, dataKey, tab }: Props) {
  const unit = UNITS[tab];

  // Filtrar valores -999 que NASA POWER usa para datos faltantes
  const cleanData = data.map(d => ({
    ...d,
    [dataKey]: Number(d[dataKey]) < -100 ? null : d[dataKey],
  }));

  // Calcular dominio real
  const values = cleanData
    .map(d => Number(d[dataKey]))
    .filter(v => v !== null && isFinite(v) && v > -100);

  const min = values.length ? Math.floor(Math.min(...values) * 0.9) : 0;
  const max = values.length ? Math.ceil(Math.max(...values) * 1.1) : 100;

  return (
    <ResponsiveContainer width="100%" height="100%">
      <AreaChart data={cleanData} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
        <defs>
          <linearGradient id="colorGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#16a34a" stopOpacity={0.15} />
            <stop offset="95%" stopColor="#16a34a" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#e8e5df" />
        <XAxis
          dataKey="fecha"
          tickFormatter={(v) => v.slice(4)}
          tick={{ fontSize: 10, fontFamily: "monospace" }}
        />
        <YAxis
          domain={[min, max]}
          tick={{ fontSize: 10, fontFamily: "monospace" }}
          tickFormatter={(v) => `${v}${unit}`}
          width={45}
        />
        <Tooltip
          labelFormatter={(v) => `Fecha: ${v}`}
          formatter={(value: unknown) => {
            const num = Number(value);
            return [isFinite(num) && num > -100 ? `${num.toFixed(1)}${unit}` : "Sin dato", tab];
          }}
        />
        <Area
          type="monotone"
          dataKey={dataKey}
          stroke="#16a34a"
          strokeWidth={2}
          fill="url(#colorGrad)"
          dot={{ r: 3, fill: "#16a34a" }}
          connectNulls={false}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}