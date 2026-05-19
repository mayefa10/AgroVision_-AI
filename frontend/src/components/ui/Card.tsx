import { HTMLAttributes } from "react";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  padding?: "none" | "sm" | "md" | "lg";
}

export function Card({ style, padding = "md", children, ...props }: CardProps) {
  const paddingMap = { none: 0, sm: "0.75rem", md: "1.25rem", lg: "2rem" };
  return (
    <div
      style={{
        borderRadius: 12,
        border: "1px solid #e8e5df",
        backgroundColor: "#ffffff",
        boxShadow: "0 1px 4px rgba(0,0,0,0.05)",
        padding: paddingMap[padding],
        ...style,
      }}
      {...props}
    >
      {children}
    </div>
  );
}