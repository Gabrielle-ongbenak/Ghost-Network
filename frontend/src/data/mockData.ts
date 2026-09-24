import type { Listing, DashboardStats, CountryBreakdown, NetworkNode, NetworkEdge } from "../types/listing"

export const dashboardStats: DashboardStats = {
  totalScanned: 8419,
  totalFlagged: 1248,
  networksDetected: 37,
  countriesMonitored: 3,
}

export const countryBreakdown: CountryBreakdown[] = [
  {
    country: "CMR",
    countryName: "Cameroon",
    flaggedCount: 524,
    percentage: 42,
    insight: "Scammers ask for an upfront 'medical clearance' fee",
  },
  {
    country: "NGA",
    countryName: "Nigeria",
    flaggedCount: 449,
    percentage: 36,
    insight: "Fake recruiters demand payment via processing fee before interview",
  },
  {
    country: "KEN",
    countryName: "Kenya",
    flaggedCount: 275,
    percentage: 22,
    insight: "Fake flight attendant job listings target job seekers",
  },
]

export const mockListings: Listing[] = [
  {
    id: "LST-9041",
    jobTitle: "Senior Rig Operations Engineer",
    entity: "Atlantic Petro Energy Ltd",
    country: "CMR",
    countryName: "Cameroon",
    platform: "Jiji Classifieds",
    riskLevel: "high",
    whyFlagged: "Same WhatsApp number used in 12 other fake ads",
    fullExplanation:
      "This listing shares a phone number with 12 other job postings across Cameroon and Nigeria, all requesting an upfront 'medical clearance' fee before interview.",
    groupId: "Group #23",
    postedAt: "2h ago",
  },
  {
    id: "LST-9038",
    jobTitle: "Executive Project Assistant",
    entity: "UNICEF Relief Mission (Spoofed Portal)",
    country: "NGA",
    countryName: "Nigeria",
    platform: "Jobberman",
    riskLevel: "high",
    whyFlagged: "Fake background check processing fee requested",
    fullExplanation:
      "Candidates are asked to pay ₦15,000 for a 'mandatory UN background check' before an interview is scheduled. UNICEF never charges application fees.",
    groupId: "Group #23",
    postedAt: "34m ago",
  },
  {
    id: "LST-9022",
    jobTitle: "Bilingual Flight Attendant (Dubai)",
    entity: "Gulf Wings Placement Agency",
    country: "KEN",
    countryName: "Kenya",
    platform: "Facebook Groups",
    riskLevel: "high",
    whyFlagged: "Requests visa processing fee via mobile money",
    fullExplanation:
      "Applicants are told to pay KES 35,000 in refundable visa fees upon arrival at Nairobi airport — a common advance-fee scam pattern.",
    groupId: "Group #14",
    postedAt: "1h ago",
  },
  {
    id: "LST-8993",
    jobTitle: "Remote Customer Support Lead",
    entity: "FinTech Global Hub LLC",
    country: "NGA",
    countryName: "Nigeria",
    platform: "Jiji Classifieds",
    riskLevel: "medium",
    whyFlagged: "Identical text matches 8 other listings",
    fullExplanation:
      "This ad's description is a near word-for-word match with 8 other 'remote customer service' listings, all requesting a security token fee before onboarding.",
    groupId: "Group #31",
    postedAt: "3h ago",
  },
  {
    id: "LST-8971",
    jobTitle: "Warehouse Logistics Supervisor",
    entity: "Douala Port Cargo S.A.",
    country: "CMR",
    countryName: "Cameroon",
    platform: "Jiji Classifieds",
    riskLevel: "medium",
    whyFlagged: "Requests refundable deposit before start date",
    fullExplanation:
      "Candidates are asked to deposit safety gear and biometric security badge fees before their first day — funds are never refunded.",
    groupId: "Group #31",
    postedAt: "5h ago",
  },
  {
    id: "LST-9002",
    jobTitle: "Hotel Front Desk & Hospitality",
    entity: "Serena Luxury Suites - Nairobi Central",
    country: "KEN",
    countryName: "Kenya",
    platform: "Corporate Website",
    riskLevel: "low",
    whyFlagged: "Standard interview schedule, direct corporate email verified",
    fullExplanation:
      "This listing follows normal hiring practices with no upfront payment requests and a verified corporate domain.",
    postedAt: "20h ago",
  },
]

export const networkNodes: NetworkNode[] = [
  { id: "LST-9041", jobTitle: "Senior Rig Operations Engineer", entity: "Atlantic Petro Energy Ltd", riskLevel: "high" },
  { id: "LST-9038", jobTitle: "Executive Project Assistant", entity: "UNICEF Relief Mission (Spoofed)", riskLevel: "high" },
  { id: "LST-9022", jobTitle: "Bilingual Flight Attendant", entity: "Gulf Wings Placement Agency", riskLevel: "high" },
  { id: "LST-9010", jobTitle: "Logistics Coordinator", entity: "West Africa Freight Co.", riskLevel: "medium" },
]

export const networkEdges: NetworkEdge[] = [
  { source: "LST-9041", target: "LST-9038", connectionType: "whatsapp", label: "Shared WhatsApp Number" },
  { source: "LST-9041", target: "LST-9022", connectionType: "text", label: "Identical Text Match" },
  { source: "LST-9038", target: "LST-9010", connectionType: "payment", label: "Same Mobile Money Account" },
]