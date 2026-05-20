"use client";
import { useState } from "react";
import { Sidebar } from "@/components/ui/Sidebar";
import { OverviewSection } from "@/components/features/OverviewSection";
import { ClimaSection } from "@/components/features/ClimaSection";
import { AgricolaSection } from "@/components/features/AgricolaSection";
import { MapSection } from "@/components/features/map/MapSection";
import { PrediccionSection } from "@/components/features/PrediccionSection";

const SECTIONS: Record<string, { title: string; component: React.ReactNode }> = {
  overview:   { title: "Resumen General",    component: <OverviewSection /> },
  clima:      { title: "Datos Climáticos",    component: <ClimaSection /> },
  agricola:   { title: "Datos Agrícolas EVA", component: <AgricolaSection /> },
  prediccion: { title: "Predicción IA",       component: <PrediccionSection /> },
};

export default function DashboardPage() {
  const [activeNav, setActiveNav] = useState("overview");
  const current = SECTIONS[activeNav];

  return (
    <div className="dashboard-wrapper">
      <Sidebar active={activeNav} onNav={setActiveNav} />
      <main className="dashboard-main">
        <div style={{
          display: "flex", justifyContent: "space-between",
          alignItems: "flex-start", marginBottom: "1.5rem",
        }}>
          <div>
            <h1 style={{ fontSize: "1.4rem", fontWeight: 700, letterSpacing: "-0.02em", marginBottom: "0.2rem" }}>
              {current.title}
            </h1>
            <p className="dashboard-topbar-sub" style={{ fontSize: "0.8rem", color: "#a1a1aa" }}>
              Fuentes: EVA · NASA POWER · DANE DIVIPOLA · OpenWeather
            </p>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", flexShrink: 0 }}>
            <div style={{ width: 8, height: 8, borderRadius: "50%", background: "#16a34a" }} />
            <span style={{ fontSize: "0.75rem", fontFamily: "monospace", color: "#16a34a" }}>En vivo</span>
          </div>
        </div>
        {current.component}
      </main>
    </div>
  );
}