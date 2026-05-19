"use client";
import { useState } from "react";
import { NAV_ITEMS } from "@/lib/constants";
import { cn } from "@/lib/utils";

interface SidebarProps {
  active: string;
  onNav: (id: string) => void;
}

export function Sidebar({ active, onNav }: SidebarProps) {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <>
      {/* Mobile toggle */}
      <button
        onClick={() => setMobileOpen(!mobileOpen)}
        style={{
          position: "fixed", top: 16, left: 16, zIndex: 60,
          width: 40, height: 40, borderRadius: 8,
          background: "#fff", border: "1px solid #e8e5df",
          cursor: "pointer", fontSize: "1.1rem",
          display: "none",
        }}
        className="mobile-menu-btn"
      >
        ☰
      </button>

      {/* Overlay mobile */}
      {mobileOpen && (
        <div
          onClick={() => setMobileOpen(false)}
          style={{ position: "fixed", inset: 0, zIndex: 55, background: "rgba(0,0,0,0.2)" }}
          className="lg:hidden"
        />
      )}

      {/* Sidebar */}
      <aside style={{
        position: "fixed",
        top: 0, left: 0,
        width: 224,
        height: "100vh",
        background: "#fff",
        borderRight: "1px solid #e8e5df",
        display: "flex",
        flexDirection: "column",
        zIndex: 56,
        overflowY: "auto",
      }}>
        {/* Logo */}
        <div style={{ padding: "1.25rem", borderBottom: "1px solid #e8e5df", display: "flex", alignItems: "center", gap: "0.6rem" }}>
          <div style={{ width: 32, height: 32, borderRadius: 8, background: "#16a34a", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "1rem" }}>
            🌾
          </div>
          <div>
            <div style={{ fontSize: "0.9rem", fontWeight: 700, letterSpacing: "-0.02em" }}>AgroVision</div>
            <div style={{ fontSize: "0.65rem", fontFamily: "monospace", color: "#a1a1aa" }}>AI Platform</div>
          </div>
        </div>

        {/* Nav */}
        <nav style={{ flex: 1, padding: "0.75rem" }}>
          <div style={{ fontSize: "0.6rem", fontFamily: "monospace", color: "#a1a1aa", letterSpacing: "0.15em", textTransform: "uppercase", padding: "0 0.5rem", marginBottom: "0.5rem" }}>
            Módulos
          </div>
          {NAV_ITEMS.map((item) => (
            <button
              key={item.id}
              onClick={() => { onNav(item.id); setMobileOpen(false); }}
              style={{
                width: "100%", textAlign: "left",
                display: "flex", alignItems: "center", gap: "0.65rem",
                padding: "0.6rem 0.75rem", borderRadius: 8,
                border: "none", cursor: "pointer",
                background: active === item.id ? "#dcfce7" : "transparent",
                color: active === item.id ? "#16a34a" : "#52525b",
                fontSize: "0.85rem", fontWeight: active === item.id ? 600 : 400,
                marginBottom: "0.15rem",
                transition: "all 0.15s",
              }}
            >
              <span>{item.icon}</span>
              {item.label}
            </button>
          ))}
        </nav>

        {/* Status */}
        <div style={{ padding: "1rem 1.25rem", borderTop: "1px solid #e8e5df" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.4rem", marginBottom: "0.2rem" }}>
            <div style={{ width: 6, height: 6, borderRadius: "50%", background: "#16a34a" }} />
            <span style={{ fontSize: "0.7rem", fontFamily: "monospace", color: "#16a34a" }}>Sistema activo</span>
          </div>
          <div style={{ fontSize: "0.65rem", color: "#a1a1aa" }}>EVA · NASA · DANE</div>
        </div>
      </aside>
    </>
  );
}