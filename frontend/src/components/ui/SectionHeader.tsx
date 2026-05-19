interface SectionHeaderProps {
  title: string;
  sub: string;
  badge?: string;
}

export function SectionHeader({ title, sub, badge }: SectionHeaderProps) {
  return (
    <div style={{ marginBottom: "1.25rem" }}>
      <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", marginBottom: "0.25rem" }}>
        <h2 style={{ fontSize: "1rem", fontWeight: 700, letterSpacing: "-0.02em", color: "#18181b" }}>
          {title}
        </h2>
        {badge && (
          <span style={{
            background: "#dcfce7", color: "#16a34a",
            padding: "0.15rem 0.5rem", borderRadius: 4,
            fontSize: "0.65rem", fontFamily: "monospace", fontWeight: 600,
          }}>
            {badge}
          </span>
        )}
      </div>
      <p style={{ fontSize: "0.8rem", color: "#a1a1aa" }}>{sub}</p>
    </div>
  );
}