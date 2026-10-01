import { LayoutDashboard, Network, List } from "lucide-react"
import Logo from "./Logo"

interface NavbarProps {
  activeTab: string
  setActiveTab: (tab: string) => void
}

const tabs = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'network', label: 'Network Graph', icon: Network },
  { id: 'listings', label: 'Listings', icon: List },
]

export default function Navbar({ activeTab, setActiveTab }: NavbarProps) {
  return (
    <aside className="w-64 h-screen bg-white dark:bg-gray-800 border-r border-gray-100 dark:border-gray-700 flex flex-col fixed left-0 top-0">
      <div className="p-6 border-b border-gray-100 dark:border-gray-700 flex items-center gap-3">
        <Logo size={40} />
        <div>
          <p className="font-bold text-gray-900 dark:text-gray-100">Ghost Networks</p>
          <p className="text-xs text-gray-400">Protecting Job Seekers</p>
        </div>
      </div>

      <nav className="flex-1 p-4 space-y-1">
        {tabs.map((tab) => {
          const Icon = tab.icon
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`w-full flex items-center gap-3 text-left px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeTab === tab.id
                  ? 'bg-emerald-600 text-white'
                  : 'text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              <Icon size={18} />
              {tab.label}
            </button>
          )
        })}
      </nav>

      <div className="p-4 border-t border-gray-100 dark:border-gray-700">
        <p className="text-sm font-medium text-gray-900 dark:text-gray-100">Amina Bello</p>
        <p className="text-xs text-gray-400">Community Safety Lead</p>
        <p className="text-xs text-gray-400 mt-1">🟢 Active Monitor: West & East Africa</p>
      </div>
    </aside>
  )
}