"use client";
import { Card } from "@/components/ui/Card";
import { SectionHeader } from "@/components/ui/SectionHeader";
import { Table } from "@/components/ui/Table";
import { useEvaData } from "@/hooks/useEvaData";
import type { EvaRow } from "@/types";

export function AgricolaSection() {
  const { data: evaData, loading } = useEvaData();

  const columns = [
    { key: "municipio", header: "Municipio", render: (r: EvaRow) => r.municipio || "—" },
    { key: "cultivo", header: "Cultivo", render: (r: EvaRow) => r.cultivo || "—" },
    {
      key: "area_sembrada",
      header: "Área Sembrada",
      className: "font-mono text-xs",
      render: (r: EvaRow) => `${Number(r.area_sembrada || 0).toLocaleString()} ha`,
    },
    {
      key: "area_cosechada",
      header: "Área Cosechada",
      className: "font-mono text-xs",
      render: (r: EvaRow) => `${Number(r.area_cosechada || 0).toLocaleString()} ha`,
    },
    {
      key: "produccion",
      header: "Producción",
      className: "font-mono text-xs",
      render: (r: EvaRow) => `${Number(r.produccion || 0).toLocaleString()} t`,
    },
    {
      key: "rendimiento",
      header: "Rendimiento",
      className: "font-mono text-xs",
      render: (r: EvaRow) => `${Number(r.rendimiento || 0).toFixed(2)} t/ha`,
    },
    {
      key: "a_o",
      header: "Año",
      className: "font-mono text-xs text-zinc-400",
      render: (r: EvaRow) => r.a_o || "—",
    },
  ];

  return (
    <div className="animate-fade-in">
      <Card>
        <SectionHeader
          title="Evaluaciones Agropecuarias — EVA"
          sub="Ministerio de Agricultura · datos.gov.co · 2019-2024"
          badge="EVA"
        />
        {evaData.length > 0 ? (
          <>
            <Table columns={columns} data={evaData} keyExtractor={(_, i) => String(i)} />
            <div className="mt-3 text-xs font-mono text-zinc-400">
              Mostrando {evaData.length} registros · Antioquia · Maíz
            </div>
          </>
        ) : (
          <div className="py-12 text-center text-zinc-400">
            {loading ? "Cargando datos EVA..." : "Sin datos disponibles"}
          </div>
        )}
      </Card>
    </div>
  );
}