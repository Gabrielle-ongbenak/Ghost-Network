import { Search, HelpCircle, Bell } from "lucide-react"
import ThemeToggle from "./ThemeToggle"

interface TopHeaderProps {
  isDark: boolean
  onToggleTheme: () => void
}

export default function TopHeader({ isDark, onToggleTheme }: TopHeaderProps) {
  return (
    <header className="h-16 bg-white dark:bg-gray-800 border-b border-gray-100 dark:border-gray-700 flex items-center justify-between px-6 gap-4">
      <div className="flex items-center gap-2 flex-1 max-w-md">
        <Search size={16} className="text-gray-400" />
        <input
          type="text"
          placeholder="Search by company, phone number..."
          className="w-full text-sm text-gray-600 placeholder-gray-400 focus:outline-none bg-transparent"
        />
      </div>

      <div className="flex items-center gap-4">
        <span className="hidden sm:flex items-center gap-1.5 text-xs text-gray-500 bg-gray-50 dark:bg-gray-700 px-3 py-1.5 rounded-full">
          <span className="w-1.5 h-1.5 rounded-full bg-green-500" />
          Scanning 3 Countries (Cameroon, Nigeria, Kenya)
        </span>

        <button className="hidden sm:flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700">
          <HelpCircle size={16} />
          Help / About
        </button>

        <ThemeToggle isDark={isDark} onToggle={onToggleTheme} />

        <button className="text-gray-400 hover:text-gray-600">
          <Bell size={18} />
        </button>

        <button
          onClick={() => alert("This feature is coming soon — it will let job seekers report suspicious listings directly.")}
          className="px-4 py-2 bg-emerald-600 text-white rounded-lg text-sm font-medium hover:bg-emerald-700 transition-colors whitespace-nowrap"
        >
        Report a Fake Job
        </button>
      </div>
    </header>
  )
}