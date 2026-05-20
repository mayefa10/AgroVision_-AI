"use client";
import { useState, useEffect } from "react";
import { NAV_ITEMS } from "@/lib/constants";

interface SidebarProps {
  active: string;
  onNav: (id: string) => void;
}

export function Sidebar({ active, onNav }: SidebarProps) {
  const [open, setOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const check = () => {
      const mobile = window.innerWidth < 1024;
      setIsMobile(mobile);
      if (!mobile) setOpen(false);
    };
    check();
    window.addEventListener("resize", check);
    return () => window.removeEventListener("resize", check);
  }, []);

  const handleNav = (id: string) => {
    onNav(id);
    setOpen(false);
  };

  const isVisible = !isMobile || open;

  return (
    <>
      {/* Hamburger — solo mobile */}
      {isMobile && (
        <button onClick={() => setOpen(!open)} style={{
          position: "fixed", top: 12, left: 12, zIndex: 80,
          width: 36, height: 36, borderRadius: 8,
          background: "#fff", border: "1px solid #e8e5df",
          cursor: "pointer", fontSize: "1rem",
          display: "flex", alignItems: "center", justifyContent: "center",
          boxShadow: "0 1px 6px rgba(0,0,0,0.1)",
        }}>
          {open ? "✕" : "☰"}
        </button>
      )}

      {/* Overlay */}
      {isMobile && open && (
        <div onClick={() => setOpen(false)} style={{
          position: "fixed", inset: 0, zIndex: 65,
          background: "rgba(0,0,0,0.3)",
        }} />
      )}

      {/* Sidebar — siempre fixed, nunca ocupa espacio en flujo */}
      <aside style={{
        position: "fixed",
        top: 0, left: 0,
        width: 224, height: "100vh",
        background: "#fff",
        borderRight: "1px solid #e8e5df",
        display: "flex", flexDirection: "column",
        zIndex: 70,
        overflowY: "auto",
        transform: isVisible ? "translateX(0)" : "translateX(-100%)",
        transition: "transform 0.25s cubic-bezier(0.4,0,0.2,1)",
        boxShadow: isMobile && open ? "4px 0 24px rgba(0,0,0,0.12)" : "none",
      }}>
        {/* Logo */}
        <div style={{
          padding: "1.25rem", borderBottom: "1px solid #e8e5df",
          display: "flex", alignItems: "center", gap: "0.6rem",
        }}>
          <div style={{
            width: 32, height: 32, borderRadius: 8, background: "#16a34a",
            display: "flex", alignItems: "center", justifyContent: "center", fontSize: "1rem",
          }}>🌾</div>
          <div>
            <div style={{ fontSize: "0.9rem", fontWeight: 700, letterSpacing: "-0.02em" }}>AgroVision</div>
            <div style={{ fontSize: "0.65rem", fontFamily: "monospace", color: "#a1a1aa" }}>AI Platform</div>
          </div>
        </div>

        {/* Nav */}
        <nav style={{ flex: 1, padding: "0.75rem" }}>
          <div style={{
            fontSize: "0.6rem", fontFamily: "monospace", color: "#a1a1aa",
            letterSpacing: "0.15em", textTransform: "uppercase",
            padding: "0 0.5rem", marginBottom: "0.5rem",
          }}>Módulos</div>
          {NAV_ITEMS.map((item) => (
            <button key={item.id} onClick={() => handleNav(item.id)} style={{
              width: "100%", textAlign: "left",
              display: "flex", alignItems: "center", gap: "0.65rem",
              padding: "0.65rem 0.75rem", borderRadius: 8,
              border: "none", cursor: "pointer", fontFamily: "inherit",
              background: active === item.id ? "#dcfce7" : "transparent",
              color: active === item.id ? "#16a34a" : "#52525b",
              fontSize: "0.85rem", fontWeight: active === item.id ? 600 : 400,
              marginBottom: "0.15rem", transition: "all 0.15s",
            }}>
              <span>{item.icon}</span>{item.label}
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