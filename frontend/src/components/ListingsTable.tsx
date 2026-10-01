import { useState } from "react"
import type { Listing} from "../types/listing"
import RiskBadge from "./RiskBadge"

const countryFlags: Record<string, string> = {
  CMR: "🇨🇲",
  NGA: "🇳🇬",
  KEN: "🇰🇪",
}


interface ListingsTableProps {
  listings: Listing[]
}

export default function ListingsTable({ listings }: ListingsTableProps) {
  const [expandedId, setExpandedId] = useState<string | null>(null)
  const [search, setSearch] = useState("")
  const [countryFilter, setCountryFilter] = useState<string>("all")
  const [riskFilter, setRiskFilter] = useState<string>("all")
  const [platformFilter, setPlatformFilter] = useState<string>("all")

  const toggleDetails = (id: string) => {
    setExpandedId(expandedId === id ? null : id)
  }

  const filteredListings = listings.filter((listing) => {
    const matchesSearch =
      listing.jobTitle.toLowerCase().includes(search.toLowerCase()) ||
      listing.entity.toLowerCase().includes(search.toLowerCase())
    const matchesCountry = countryFilter === "all" || listing.country === countryFilter
    const matchesRisk = riskFilter === "all" || listing.riskLevel === riskFilter
const matchesPlatform = platformFilter === "all" || listing.platform === platformFilter
return matchesSearch && matchesCountry && matchesRisk && matchesPlatform
  })
    const exportToCSV = () => {
    const headers = ["Job Title", "Company", "Country", "Platform", "Risk Level", "Why Flagged"]
    const rows = filteredListings.map((l) => [
      l.jobTitle,
      l.entity,
      l.countryName,
      l.platform,
      l.riskLevel,
      l.whyFlagged,
    ])

    const csvContent = [headers, ...rows]
      .map((row) => row.map((cell) => `"${cell}"`).join(","))
      .join("\n")

    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" })
    const url = URL.createObjectURL(blob)
    const link = document.createElement("a")
    link.href = url
    link.setAttribute("download", "ghost-networks-flagged-listings.csv")
    document.body.appendChild(link)
    link.click()
   document.body.removeChild(link)
  }

  return (<div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
      <div className="p-6 border-b border-gray-100">
        <h2 className="text-lg font-bold text-gray-900">Most Suspicious Job Listings</h2>
        <p className="text-sm text-gray-500 mt-1">
          Recent job posts flagged by our system that require immediate caution.
        </p>
                <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-gray-900">Most Suspicious Job Listings</h2>
            <p className="text-sm text-gray-500 mt-1">
              Recent job posts flagged by our system that require immediate caution.
            </p>
          </div>
          <button
            onClick={exportToCSV}
            className="px-4 py-2 bg-gray-900 text-white rounded-lg text-sm font-medium hover:bg-gray-700 transition-colors whitespace-nowrap"
          >
            Export CSV
          </button>
        </div>

        <div className="flex flex-col sm:flex-row gap-3 mt-4">
          <input
            type="text"
            placeholder="Search by job title or company..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="flex-1 px-4 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
          />
          <select
            value={countryFilter}
            onChange={(e) => setCountryFilter(e.target.value)}
            className="px-4 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
          >
            <option value="all">All Countries</option>
            <option value="CMR">Cameroon</option>
            <option value="NGA">Nigeria</option>
            <option value="KEN">Kenya</option>
          </select>
          <select
            value={riskFilter}
            onChange={(e) => setRiskFilter(e.target.value)}
            className="px-4 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
          >
            <option value="all">All Risk Levels</option>
            <option value="high">High Risk</option>
            <option value="medium">Medium Risk</option>
            <option value="low">Low Risk</option>
          </select>
                    <select
            value={platformFilter}
            onChange={(e) => setPlatformFilter(e.target.value)}
            className="px-4 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
          >
            <option value="all">All Platforms</option>
            <option value="Jiji Classifieds">Jiji Classifieds</option>
            <option value="Jobberman">Jobberman</option>
            <option value="Facebook Groups">Facebook Groups</option>
            <option value="Corporate Website">Corporate Website</option>
          </select>
                    <button
          onClick={() => {
            setSearch("")
            setCountryFilter("all")
            setRiskFilter("all")
            setPlatformFilter("all")
}}
            className="px-4 py-2 text-sm font-medium text-gray-500 hover:text-gray-700 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Reset Filters
          </button>
        </div>
      </div>

      {filteredListings.length === 0 ? (
        <div className="p-8 text-center text-gray-400">
          No listings match your search or filters.
        </div>
      ) : (
        <table className="w-full text-left">
          <thead>
            <tr className="text-xs text-gray-400 uppercase border-b border-gray-100">
              <th className="px-6 py-3 font-medium">Job Title & Company</th>
              <th className="px-6 py-3 font-medium">Country</th>
              <th className="px-6 py-3 font-medium">Platform</th>
              <th className="px-6 py-3 font-medium">Risk Level</th>
              <th className="px-6 py-3 font-medium">Why it's suspicious</th>
              <th className="px-6 py-3 font-medium">Action</th>
            </tr>
          </thead>
          <tbody>
            {filteredListings.map((listing) => (
              <>
                <tr key={listing.id} className="border-b border-gray-50 hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4">
                    <p className="font-medium text-gray-900">{listing.jobTitle}</p>
                    <p className="text-sm text-gray-400">{listing.entity}</p>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">
  {countryFlags[listing.country]} {listing.countryName}
</td>
                  <td className="px-6 py-4 text-sm text-gray-600">{listing.platform}</td>
                  <td className="px-6 py-4">
                    <RiskBadge level={listing.riskLevel} />
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600 max-w-xs">{listing.whyFlagged}</td>
                  <td className="px-6 py-4">
                    <button
  onClick={() => toggleDetails(listing.id)}
  className="inline-block px-3 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 hover:bg-emerald-100 transition-colors"
>
  {expandedId === listing.id ? "Hide Details" : "View Details"}
                </button>
                  </td>
                </tr>
                {expandedId === listing.id && listing.fullExplanation && (
                  <tr key={`${listing.id}-details`} className="bg-blue-50">
                    <td colSpan={6} className="px-6 py-4 text-sm text-gray-700">
                      <strong>Full explanation:</strong> {listing.fullExplanation}
                      {listing.groupId && (
                        <span className="ml-2 text-gray-400">— Linked to {listing.groupId}</span>
                      )}
                    </td>
                  </tr>
                )}
              </>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}