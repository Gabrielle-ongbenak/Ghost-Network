import type { RiskLevel } from "../types/listing"

interface RiskBadgeProps {
  level: RiskLevel
}

const styles: Record<RiskLevel, string> = {
  high: "bg-red-100 text-red-700",
  medium: "bg-orange-100 text-orange-700",
  low: "bg-green-100 text-green-700",
}

const labels: Record<RiskLevel, string> = {
  high: "High Risk",
  medium: "Medium Risk",
  low: "Low Risk",
}

export default function RiskBadge({ level }: RiskBadgeProps) {
  return (
    <span className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${styles[level]}`}>
      {labels[level]}
    </span>
  )
}