import { Card } from "./Card";
import type { KpiData } from "@/types";

interface KpiCardProps extends KpiData {}

export function KpiCard({ label, value, sub, color = "#16a34a", icon }: KpiCardProps) {
  return (
    <Card style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <span style={{ fontSize: "0.75rem", fontWeight: 500, color: "#a1a1aa" }}>{label}</span>
        <span style={{ fontSize: "1.25rem" }}>{icon}</span>
      </div>
      <div style={{ fontSize: "2rem", fontWeight: 700, lineHeight: 1, color }}>
        {value}
      </div>
      <div style={{ fontSize: "0.72rem", color: "#a1a1aa" }}>{sub}</div>
    </Card>
  );
}