"use client";

import { useState } from "react";
import { Card } from "@/components/ui/Card";
import { SectionHeader } from "@/components/ui/SectionHeader";
import { Table } from "@/components/ui/Table";
import { useEvaData } from "@/hooks/useEvaData";
import type { EvaRow } from "@/types";

// ── Opciones de filtro ────────────────────────────────────

const DEPARTAMENTOS = [
  "ANTIOQUIA", "ATLANTICO", "BOLIVAR", "BOYACA", "CALDAS",
  "CAQUETA", "CAUCA", "CESAR", "CHOCO", "CORDOBA",
  "CUNDINAMARCA", "GUAJIRA", "HUILA", "MAGDALENA", "META",
  "NARINO", "NORTE DE SANTANDER", "SANTANDER", "SUCRE",
  "TOLIMA", "VALLE DEL CAUCA",
];

const CULTIVOS = [
  "Todos", "MAIZ", "ARROZ", "PAPA", "CAFE", "FRIJOL",
  "YUCA", "CANA DE AZUCAR", "PLATANO", "CACAO", "SORGO",
  "SOYA", "PALMA", "AGUACATE", "TOMATE",
];

// ── Helpers de formato ─────────────────────────────────────
// Muestran "—" cuando el valor es null/undefined en vez de "0 ha"

function fmtArea(val?: number | null): string {
  if (val == null) return "—";
  return `${Number(val).toLocaleString("es-CO")} ha`;
}

function fmtTon(val?: number | null): string {
  if (val == null) return "—";
  return `${Number(val).toLocaleString("es-CO")} t`;
}

function fmtRend(val?: number | null): string {
  if (val == null) return "—";
  return `${Number(val).toFixed(2)} t/ha`;
}

function toTitleCase(str?: string): string {
  if (!str) return "—";
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}

// ── Columnas de la tabla ──────────────────────────────────

const columns = [
  {
    key: "municipio",
    header: "Municipio",
    render: (r: EvaRow) => toTitleCase(r.municipio),
  },
  {
    key: "cultivo",
    header: "Cultivo",
    render: (r: EvaRow) => toTitleCase(r.cultivo),
  },
  {
    key: "area_sembrada",
    header: "Área Sembrada",
    className: "font-mono text-xs",
    render: (r: EvaRow) => fmtArea(r.area_sembrada),   // sin || 0
  },
  {
    key: "area_cosechada",
    header: "Área Cosechada",
    className: "font-mono text-xs",
    render: (r: EvaRow) => fmtArea(r.area_cosechada),  // sin || 0
  },
  {
    key: "produccion",
    header: "Producción",
    className: "font-mono text-xs",
    render: (r: EvaRow) => fmtTon(r.produccion),       // sin || 0
  },
  {
    key: "rendimiento",
    header: "Rendimiento",
    className: "font-mono text-xs",
    render: (r: EvaRow) => fmtRend(r.rendimiento),
  },
  {
    key: "anio",
    header: "Año",
    className: "font-mono text-xs text-zinc-400",
    render: (r: EvaRow) => String(r.anio ?? r.a_o ?? "—"),
  },
];

// ── Componente ────────────────────────────────────────────

export function AgricolaSection() {
  const [departamento, setDepartamento] = useState("ANTIOQUIA");
  const [cultivo, setCultivo]           = useState("Todos");

  const cultivoParam                            = cultivo === "Todos" ? undefined : cultivo;
  const { data: evaData, loading, totalRegistros } = useEvaData(departamento, cultivoParam);

  const labelDpto    = toTitleCase(departamento);
  const labelCultivo = cultivo === "Todos" ? "todos los cultivos" : toTitleCase(cultivo);

  return (
    <div className="animate-fade-in space-y-4">
      <Card>
        <SectionHeader
          title="Evaluaciones Agropecuarias — EVA"
          sub="Ministerio de Agricultura · datos.gov.co · 2019-2024"
          badge="EVA"
        />

        {/* ── Filtros ── */}
        <div className="flex flex-wrap gap-3 mb-4">

          {/* Departamento */}
          <div className="flex flex-col gap-1">
            <label
              htmlFor="eva-departamento"
              className="text-xs text-zinc-400 font-medium uppercase tracking-wide"
            >
              Departamento
            </label>
            <select
              id="eva-departamento"
              name="eva-departamento"
              aria-label="Filtrar por departamento"
              value={departamento}
              onChange={(e) => setDepartamento(e.target.value)}
              className="
                bg-zinc-900 border border-zinc-700 rounded-md
                px-3 py-1.5 text-sm text-zinc-100
                focus:outline-none focus:ring-1 focus:ring-emerald-500
                cursor-pointer min-w-[180px]
              "
            >
              {DEPARTAMENTOS.map((d) => (
                <option key={d} value={d}>
                  {toTitleCase(d)}
                </option>
              ))}
            </select>
          </div>

          {/* Cultivo */}
          <div className="flex flex-col gap-1">
            <label
              htmlFor="eva-cultivo"
              className="text-xs text-zinc-400 font-medium uppercase tracking-wide"
            >
              Cultivo
            </label>
            <select
              id="eva-cultivo"
              name="eva-cultivo"
              aria-label="Filtrar por cultivo"
              value={cultivo}
              onChange={(e) => setCultivo(e.target.value)}
              className="
                bg-zinc-900 border border-zinc-700 rounded-md
                px-3 py-1.5 text-sm text-zinc-100
                focus:outline-none focus:ring-1 focus:ring-emerald-500
                cursor-pointer min-w-[140px]
              "
            >
              {CULTIVOS.map((c) => (
                <option key={c} value={c}>
                  {c === "Todos" ? "Todos los cultivos" : toTitleCase(c)}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* ── Tabla ── */}
        {loading ? (
          <div className="py-12 text-center text-zinc-400 animate-pulse">
            Cargando datos EVA...
          </div>
        ) : evaData.length > 0 ? (
          <>
            <Table
              columns={columns}
              data={evaData}
              keyExtractor={(_, i) => String(i)}
            />
            <div className="mt-3 text-xs font-mono text-zinc-400 flex justify-between items-center">
              <span>
                Mostrando {evaData.length}
                {totalRegistros != null ? ` de ${totalRegistros}` : ""} registros
              </span>
              <span className="text-zinc-500">
                {labelDpto} · {labelCultivo}
              </span>
            </div>
          </>
        ) : (
          <div className="py-12 text-center text-zinc-400">
            Sin datos para{" "}
            <span className="text-zinc-200">{labelDpto}</span>
            {cultivo !== "Todos" && (
              <> — <span className="text-zinc-200">{toTitleCase(cultivo)}</span></>
            )}
          </div>
        )}
      </Card>
    </div>
  );
}