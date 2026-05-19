import { cn } from "@/lib/utils";

interface TabsProps<T extends string> {
  items: readonly T[];
  active: T;
  onChange: (value: T) => void;
}

export function Tabs<T extends string>({ items, active, onChange }: TabsProps<T>) {
  return (
    <div style={{ display: "flex", gap: "0.25rem", marginBottom: "1.25rem" }}>
      {items.map((item) => (
        <button
          key={item}
          onClick={() => onChange(item)}
          style={{
            padding: "0.4rem 1rem",
            borderRadius: 6,
            border: `1px solid ${active === item ? "#18181b" : "#e8e5df"}`,
            background: active === item ? "#18181b" : "transparent",
            color: active === item ? "#ffffff" : "#52525b",
            fontSize: "0.78rem",
            fontWeight: active === item ? 600 : 400,
            cursor: "pointer",
            transition: "all 0.15s",
            fontFamily: "inherit",
          }}
        >
          {item}
        </button>
      ))}
    </div>
  );
}