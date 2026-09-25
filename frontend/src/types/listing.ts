export type RiskLevel = "high" | "medium" | "low"

export interface Listing {
  id: string
  jobTitle: string
  entity: string
  country: "CMR" | "NGA" | "KEN"
  countryName: string
  platform: string
  riskLevel: RiskLevel
  whyFlagged: string
  fullExplanation?: string
  groupId?: string
  postedAt: string
}

export interface DashboardStats {
  totalScanned: number
  totalFlagged: number
  networksDetected: number
  countriesMonitored: number
}

export interface CountryBreakdown {
  country: "CMR" | "NGA" | "KEN"
  countryName: string
  flaggedCount: number
  percentage: number
  insight: string
}

export interface NetworkNode {
  id: string
  jobTitle: string
  entity: string
  riskLevel: RiskLevel
}

export interface NetworkEdge {
  source: string
  target: string
  connectionType: "phone" | "text" | "whatsapp" | "payment"
  label: string
}