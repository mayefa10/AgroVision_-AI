import { RISK_BG, RISK_COLORS, RISK_LABELS } from "@/lib/constants";
import type { RiskLevel } from "@/types";

interface RiskBadgeProps {
  level: RiskLevel;
}

export function RiskBadge({ level }: RiskBadgeProps) {
  return (
    <span
      className="inline-flex items-center rounded-full px-2.5 py-0.5 text-[0.7rem] font-semibold uppercase tracking-wider font-mono"
      style={{
        backgroundColor: RISK_BG[level],
        color: RISK_COLORS[level],
      }}
    >
      {RISK_LABELS[level]}
    </span>
  );
}