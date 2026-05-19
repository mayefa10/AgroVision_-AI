"use client";
import { ButtonHTMLAttributes } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  size?: "sm" | "md" | "lg";
  variant?: "primary" | "ghost";
  isLoading?: boolean;
}

export function Button({
  children, size = "md", variant = "primary",
  isLoading, disabled, style, ...props
}: ButtonProps) {
  const pad = size === "lg" ? "0.875rem 1.5rem" : size === "sm" ? "0.4rem 0.875rem" : "0.6rem 1.25rem";
  const fs = size === "lg" ? "0.9rem" : size === "sm" ? "0.75rem" : "0.82rem";

  return (
    <button
      disabled={disabled || isLoading}
      style={{
        width: "100%",
        padding: pad,
        fontSize: fs,
        fontWeight: 600,
        fontFamily: "inherit",
        borderRadius: 8,
        border: variant === "ghost" ? "1px solid #e8e5df" : "none",
        background: variant === "ghost" ? "transparent" : "#18181b",
        color: variant === "ghost" ? "#52525b" : "#ffffff",
        cursor: (disabled || isLoading) ? "not-allowed" : "pointer",
        opacity: (disabled || isLoading) ? 0.6 : 1,
        transition: "all 0.15s",
        display: "flex", alignItems: "center", justifyContent: "center", gap: "0.5rem",
        ...style,
      }}
      {...props}
    >
      {isLoading ? "Calculando..." : children}
    </button>
  );
}