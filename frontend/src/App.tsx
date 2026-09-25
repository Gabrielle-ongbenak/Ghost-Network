import KPICard from "./components/KPICard"
import ListingsTable from "./components/ListingsTable"
import { dashboardStats, mockListings } from "./data/mockData"

function App() {
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-2xl font-bold text-gray-900 mb-1">
          Ghost Networks — Detecting Job Scam Networks in Africa
        </h1>
        <p className="text-gray-500 mb-8">
          We track how seemingly separate fake job postings are secretly
          connected by the same phone numbers, payment accounts, and scammers.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <KPICard
            label="Total Listings Scanned"
            value={dashboardStats.totalScanned.toLocaleString()}
            description="Monitored across African job platforms over the last 30 days."
            accentColor="blue"
          />
          <KPICard
            label="Scam Networks Found"
            value={dashboardStats.networksDetected}
            description="Groups of fake job ads working together using the same contacts."
            accentColor="red"
          />
          <KPICard
            label="Countries Monitored"
            value={dashboardStats.countriesMonitored}
            description="Active surveillance across Cameroon, Nigeria, and Kenya."
            accentColor="green"
          />
        </div>

        <ListingsTable listings={mockListings} />
      </div>
    </div>
  )
}

export default App