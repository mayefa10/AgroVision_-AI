"use client";
import { useEffect, useRef } from "react";
import type { Region } from "@/types";

interface Props {
  regions: Region[];
  onRegionClick?: (region: Region) => void;
}

const RISK_COLORS = {
  low:      "#22c55e",
  medium:   "#f59e0b",
  high:     "#f97316",
  critical: "#ef4444",
};

const RISK_LABELS = {
  low: "Bajo", medium: "Medio", high: "Alto", critical: "Crítico"
};

export function ColombiaMap({ regions, onRegionClick }: Props) {
  const mapRef = useRef<any>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;

    // Importar Leaflet solo en cliente
    import("leaflet").then((L) => {
      // Fix icono por defecto de Leaflet en Next.js
      delete (L.Icon.Default.prototype as any)._getIconUrl;
      L.Icon.Default.mergeOptions({
        iconRetinaUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png",
        iconUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png",
        shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png",
      });

      // Inicializar mapa centrado en Colombia
      const map = L.map(containerRef.current!, {
        center: [4.5709, -74.2973],
        zoom: 5,
        zoomControl: true,
        scrollWheelZoom: true,
      });

      mapRef.current = map;

      // Tile layer — OpenStreetMap
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: '© <a href="https://openstreetmap.org">OpenStreetMap</a>',
        maxZoom: 18,
      }).addTo(map);

      // Agregar marcadores por región
      regions.forEach((region) => {
        const color = RISK_COLORS[region.risk];
        const label = RISK_LABELS[region.risk];

        // Círculo de fondo (pulso)
        const pulseCircle = L.circleMarker([region.lat, region.lng], {
          radius: 22,
          fillColor: color,
          fillOpacity: 0.15,
          color: color,
          weight: 1,
          opacity: 0.4,
        }).addTo(map);

        // Círculo principal
        const circle = L.circleMarker([region.lat, region.lng], {
          radius: 12,
          fillColor: color,
          fillOpacity: 0.9,
          color: "#ffffff",
          weight: 2,
          opacity: 1,
        }).addTo(map);

        // Popup con info
        const popupContent = `
          <div style="font-family: system-ui, sans-serif; min-width: 160px;">
            <div style="font-weight: 700; font-size: 0.9rem; margin-bottom: 4px;">${region.region}</div>
            <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 4px;">
              <div style="width: 8px; height: 8px; border-radius: 50%; background: ${color};"></div>
              <span style="font-size: 0.8rem; color: ${color}; font-weight: 600;">Riesgo ${label}</span>
            </div>
            <div style="font-size: 0.72rem; color: #888; font-family: monospace;">Código: ${region.code}</div>
          </div>
        `;

        circle.bindPopup(popupContent, {
          closeButton: false,
          className: "agrovision-popup",
        });

        circle.on("mouseover", () => circle.openPopup());
        circle.on("mouseout", () => circle.closePopup());
        circle.on("click", () => {
          if (onRegionClick) onRegionClick(region);
        });
      });
    });

    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
    };
  }, [regions]);

  return (
    <>
      <style>{`
        @import url('https://unpkg.com/leaflet@1.9.4/dist/leaflet.css');
        .agrovision-popup .leaflet-popup-content-wrapper {
          border-radius: 10px;
          box-shadow: 0 4px 20px rgba(0,0,0,0.12);
          border: 1px solid #e8e5df;
          padding: 0;
        }
        .agrovision-popup .leaflet-popup-content {
          margin: 12px 14px;
        }
        .agrovision-popup .leaflet-popup-tip {
          background: white;
        }
        .leaflet-container {
          font-family: system-ui, sans-serif;
          border-radius: 12px;
        }
      `}</style>
      <div
        ref={containerRef}
        style={{ width: "100%", height: "100%", borderRadius: 12, zIndex: 0 }}
      />
    </>
  );
}