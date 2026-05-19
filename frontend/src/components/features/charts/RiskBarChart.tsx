"use client";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { RISK_COLORS, RISK_LABELS } from "@/lib/constants";
import type { Region, RiskLevel } from "@/types";

interface Props {
  regions: Region[];
}

export function RiskBarChart({ regions }: Props) {
  const data = regions.map((r) => ({
    name: r.region.length > 8 ? r.region.slice(0, 8) + "." : r.region,
    riesgo: r.risk === "critical" ? 4 : r.risk === "high" ? 3 : r.risk === "medium" ? 2 : 1,
    color: RISK_COLORS[r.risk],
    full: r.region,
    risk: r.risk,
  }));

  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={data} barSize={20}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e8e5df" />
        <XAxis dataKey="name" tick={{ fontSize: 10, fontFamily: "var(--font-mono)" }} />
        <YAxis
          domain={[0, 4]}
          ticks={[1, 2, 3, 4]}
          tickFormatter={(v) => ["", "Bajo", "Medio", "Alto", "Crítico"][v]}
          tick={{ fontSize: 9, fontFamily: "var(--font-mono)" }}
        />
        <Tooltip
          formatter={(_v, _n, props: any) => [
            RISK_LABELS[props.payload.risk as RiskLevel],
            "Riesgo",
          ]}
          labelFormatter={(_l, p: any) => p?.[0]?.payload?.full || ""}
        />
        <Bar dataKey="riesgo" radius={[4, 4, 0, 0]}>
          {data.map((entry, i) => (
            <Cell key={i} fill={entry.color} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}