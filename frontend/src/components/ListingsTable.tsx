import { useState } from "react"
import type { Listing } from "../types/listing"
import RiskBadge from "./RiskBadge"

interface ListingsTableProps {
  listings: Listing[]
}

export default function ListingsTable({ listings }: ListingsTableProps) {
  const [expandedId, setExpandedId] = useState<string | null>(null)

  const toggleDetails = (id: string) => {
    setExpandedId(expandedId === id ? null : id)
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div className="p-6 border-b border-gray-100">
        <h2 className="text-lg font-bold text-gray-900">Most Suspicious Job Listings</h2>
        <p className="text-sm text-gray-500 mt-1">
          Recent job posts flagged by our system that require immediate caution.
        </p>
      </div>

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
          {listings.map((listing) => (
            <>
              <tr key={listing.id} className="border-b border-gray-50 hover:bg-gray-50 transition-colors">
                <td className="px-6 py-4">
                  <p className="font-medium text-gray-900">{listing.jobTitle}</p>
                  <p className="text-sm text-gray-400">{listing.entity}</p>
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">{listing.countryName}</td>
                <td className="px-6 py-4 text-sm text-gray-600">{listing.platform}</td>
                <td className="px-6 py-4">
                  <RiskBadge level={listing.riskLevel} />
                </td>
                <td className="px-6 py-4 text-sm text-gray-600 max-w-xs">{listing.whyFlagged}</td>
                <td className="px-6 py-4">
                  <button
                    onClick={() => toggleDetails(listing.id)}
                    className="text-blue-600 text-sm font-medium hover:underline"
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
    </div>
  )
}