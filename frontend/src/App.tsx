import { useState, useEffect } from 'react'
import ThemeToggle from './components/ThemeToggle'
import TopHeader from './components/TopHeader'
import Navbar from './components/Navbar'
import KPICard from './components/KPICard'
import CountryChart from './components/CountryChart'
import PlatformChart from './components/PlatformChart'
import ListingsTable from './components/ListingsTable'
import NetworkGraphView from './components/NetworkGraphView'
import SafetyBanner from './components/SafetyBanner'
import { api } from './services/api'
import type { Listing, DashboardStats, CountryBreakdown, NetworkNode, NetworkEdge } from './types/listing'

function App() {
  const [activeTab, setActiveTab] = useState('dashboard')
  const [isDark, setIsDark] = useState(() => localStorage.getItem('theme') === 'dark')

useEffect(() => {
  document.documentElement.classList.toggle('dark', isDark)
  localStorage.setItem('theme', isDark ? 'dark' : 'light')
}, [isDark])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [dashboardStats, setDashboardStats] = useState<DashboardStats | null>(null)
  const [countryBreakdown, setCountryBreakdown] = useState<CountryBreakdown[]>([])
  const [platformBreakdown, setPlatformBreakdown] = useState<any[]>([])
  const [mockListings, setListings] = useState<Listing[]>([])
  const [networkNodes, setNetworkNodes] = useState<NetworkNode[]>([])
  const [networkEdges, setNetworkEdges] = useState<NetworkEdge[]>([])

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true)
        const [stats, countries, platforms, listings, nodes, edges] = await Promise.all([
          api.getDashboardStats(),
          api.getCountryBreakdown(),
          api.getPlatformBreakdown(),
          api.getListings(),
          api.getNetworkNodes(),
          api.getNetworkEdges(),
        ])
        setDashboardStats(stats)
        setCountryBreakdown(countries)
        setPlatformBreakdown(platforms)
        setListings(listings)
        setNetworkNodes(nodes)
        setNetworkEdges(edges)
      } catch (err) {
        setError("Failed to load data. Please try again.")
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-gray-400">Loading Ghost Networks dashboard...</p>
      </div>
    )
  }

  if (error || !dashboardStats) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-red-500">{error || "Something went wrong."}</p>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 transition-colors">
            <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

      <div className="ml-64">
        <TopHeader isDark={isDark} onToggleTheme={() => setIsDark(!isDark)} />
        <main className="max-w-7xl px-4 sm:px-6 lg:px-8 py-8 transition-opacity duration-300 ease-in-out">
       {activeTab === 'dashboard' && (
  <div key="dashboard" className="space-y-8 animate-fadeIn">
            <div>
              <h1 className="text-2xl font-extrabold text-gray-900 tracking-tight"  >
                Ghost Networks — Detecting Job Scam Networks in Africa
              </h1>
              <p className="text-sm text-gray-500 mt-1">
                We track how seemingly separate fake job postings are secretly connected by the same phone numbers, payment accounts, and scammers.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <KPICard
                label="Total Listings Scanned"
                value={dashboardStats.totalScanned.toLocaleString()}
                description="Monitored across African job platforms over the last 30 days."
                accentColor="blue"
              />
              <KPICard
                label="Scam Networks Found"
                value={dashboardStats.networksDetected}
                description="Organized multi-job networks connecting flagged ads."
                accentColor="red"
                subStats={[
                  { label: "Active Rings", value: String((dashboardStats as any).activeRings ?? "-"), color: "red" },
                  { label: "Flagged for Takedown", value: String((dashboardStats as any).flaggedForTakedown ?? "-"), color: "gray" },
                ]}
              />
              <KPICard
                label="Countries Monitored"
                value={dashboardStats.countriesMonitored}
                description="Active surveillance across Cameroon, Nigeria, and Kenya."
                accentColor="green"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <CountryChart data={countryBreakdown} />
              <PlatformChart data={platformBreakdown} />
            </div>
            
          </div>
        )}
{activeTab === 'listings' && (
  <div key="listings" className="space-y-6 animate-fadeIn">
            <div>
              <h1  className="text-2xl font-extrabold text-gray-900 tracking-tight">Scam Job Directory </h1>
              <p className="text-sm text-gray-500 mt-1">
                Search and inspect job postings flagged by Ghost Networks.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <KPICard
                label="Flagged Suspicious Listings"
                value={dashboardStats.totalFlagged.toLocaleString()}
                description={`Out of ${dashboardStats.totalScanned.toLocaleString()} total scanned.`}
                accentColor="red"
              />
              <KPICard
                label="Syndicate Rings Mapped"
                value={dashboardStats.networksDetected}
                description="Multi-country groups"
                accentColor="blue"
              />
              <KPICard
                label="Upfront Fees Intercepted"
                value={String((dashboardStats as any).upfrontFeesIntercepted ?? "-")}
                description="Estimated seeker loss averted"
                accentColor="green"
              />
              <KPICard
                label="Platform Takedown Rate"
                value={String((dashboardStats as any).platformTakedownRate ?? "-")}
                description="Listings deleted"
                accentColor="blue"
              />
            </div>

            <ListingsTable listings={mockListings} />
            <SafetyBanner />
          </div>
        )}
{activeTab === 'network' && (
  <div key="network" className="space-y-6 animate-fadeIn">cd frontend
            <div>
              <h1 className="text-2xl font-extrabold text-gray-900 tracking-tight">How Fake Jobs Are Secretly Connected</h1>
              <p className="text-sm text-gray-500 mt-1">
                This visual map shows how seemingly unrelated ads share the same contacts.
              </p>
            </div>
            <NetworkGraphView nodes={networkNodes} edges={networkEdges} />
            <SafetyBanner />
          </div>
          )}
        </main>
      </div>
    </div>
  )
}

export default App