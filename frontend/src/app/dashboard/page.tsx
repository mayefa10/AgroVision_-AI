"use client";
import { useState } from "react";
import { Sidebar } from "@/components/ui/Sidebar";
import { OverviewSection } from "@/components/features/OverviewSection";
import { ClimaSection } from "@/components/features/ClimaSection";
import { AgricolaSection } from "@/components/features/AgricolaSection";
import { MapSection } from "@/components/features/map/MapSection";
import { AlertasSection } from "@/components/features/AlertasSection";
import { PrediccionSection } from "@/components/features/PrediccionSection";
import { OpenWeatherSection } from "@/components/features/OpenWeatherSection";
import { EnsoSection }        from "@/components/features/EnsoSection";
import { EscenariosSection }  from "@/components/features/EscenariosSection";

const SECTIONS: Record<string, { title: string; component: React.ReactNode }> = {
  overview: { title: "Resumen General", component: <OverviewSection /> },
  clima: { title: "Datos Climáticos", component: <ClimaSection /> },
  agricola: { title: "Datos Agrícolas EVA", component: <AgricolaSection /> },
  alertas: { title: "Alertas Climáticas", component: <AlertasSection /> },
  mapa: { title: "Mapa de Riesgo", component: <MapSection /> },
  prediccion: { title: "Predicción IA", component: <PrediccionSection /> },
  enso:        { title: "Monitor ENSO",   component: <EnsoSection /> },
  openweather: { title: "Tiempo Real",    component: <OpenWeatherSection /> },
  escenarios:  { title: "Escenarios IA",  component: <EscenariosSection /> },

};

export default function DashboardPage() {
  const [activeNav, setActiveNav] = useState("overview");
  const current = SECTIONS[activeNav] ?? SECTIONS["overview"];

  return (
    <div className="dashboard-wrapper">
      <Sidebar active={activeNav} onNav={setActiveNav} />
      <main className="dashboard-main">
        <div style={{ display: "flex", justifyContent: "space-between",
          alignItems: "flex-start", marginBottom: "1.5rem" }}>
          <div>
            <h1 style={{ fontSize: "1.4rem", fontWeight: 700,
              letterSpacing: "-0.02em", marginBottom: "0.2rem" }}>
              {current.title}
            </h1>
            <p style={{ fontSize: "0.8rem", color: "#a1a1aa" }}>
              Fuentes: EVA · NASA POWER · DANE DIVIPOLA · OpenWeather · NOAA
            </p>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <div style={{ width: 8, height: 8, borderRadius: "50%", background: "#16a34a" }} />
            <span style={{ fontSize: "0.75rem", fontFamily: "monospace", color: "#16a34a" }}>
              En vivo
            </span>
          </div>
        </div>
        {current.component}
      </main>
    </div>
  );
}