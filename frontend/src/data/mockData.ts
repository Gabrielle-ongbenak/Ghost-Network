import type { Listing, CountryBreakdown, NetworkEdge } from "../types/listing"

export const dashboardStats = {
  totalScanned: 8419,
  totalFlagged: 1248,
  networksDetected: 37,
  countriesMonitored: 3,
  activeRings: 18,
  flaggedForTakedown: 19,
  upfrontFeesIntercepted: "$84.2k",
  platformTakedownRate: "78.4%",
  listingsDeleted: 976,
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
export const platformBreakdown = [
  { platform: "Jiji Classifieds", count: 612, percentage: 49, riskLevel: "high" as const },
  { platform: "Jobberman", count: 386, percentage: 31, riskLevel: "high" as const },
  { platform: "Facebook Groups", count: 250, percentage: 20, riskLevel: "medium" as const },
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

export const networkNodes = [
  { id: "LST-9041", jobTitle: "Rig Engineer Ad", entity: "Atlantic Petro Corp", riskLevel: "high" as const, x: 25, y: 25 },
  { id: "LST-9038", jobTitle: "UNICEF Aid Ad", entity: "Spoofed NGO", riskLevel: "high" as const, x: 70, y: 20 },
  { id: "LST-9022", jobTitle: "Flight Attendant Ad", entity: "Gulf Wings Crew Services", riskLevel: "high" as const, x: 75, y: 70 },
  { id: "LST-9010", jobTitle: "Warehouse Clerk Ad", entity: "Gulf Terminal Support Co.", riskLevel: "medium" as const, x: 25, y: 70 },
]

export const networkEdges: NetworkEdge[] = [
  { source: "LST-9041", target: "LST-9038", connectionType: "whatsapp", label: "Shared WhatsApp Number" },
  { source: "LST-9041", target: "LST-9022", connectionType: "text", label: "Identical Text Match" },
  { source: "LST-9038", target: "LST-9010", connectionType: "payment", label: "Same Mobile Money Account" },
]
export const networkGroupInfo = {
  groupId: "Group #49",
  status: "Active Syndicate",
  simpleExplanation: "This single group of scammers posted 14 different job ads across Cameroon, Nigeria, and Kenya. Every ad instructs job applicants to contact the exact same WhatsApp number to pay a fake 'application fee'.",
  totalConnectedAds: 14,
  countriesTargeted: [
    { name: "Cameroon", count: 6 },
    { name: "Nigeria", count: 5 },
    { name: "Kenya", count: 3 },
  ],
  sharedWhatsApp: "+237 6 78 49 11 20",
  commonScamTrick: "Demanding upfront $45 USD / 15,000 NGN fee for a fake 'medical kit' or 'clearance badge'.",
}