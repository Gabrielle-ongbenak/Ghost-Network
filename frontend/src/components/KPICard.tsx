interface KPICardProps {
  label: string
  value: string | number
  description: string
  accentColor?: "blue" | "red" | "green"
}

export default function KPICard({ label, value, description, accentColor = "blue" }: KPICardProps) {
  const colorClasses = {
    blue: "text-blue-600",
    red: "text-red-600",
    green: "text-green-600",
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <p className="text-sm font-medium text-gray-500">{label}</p>
      <p className={`text-4xl font-bold mt-2 ${colorClasses[accentColor]}`}>
        {value}
      </p>
      <p className="text-sm text-gray-400 mt-2">{description}</p>
    </div>
  )
}