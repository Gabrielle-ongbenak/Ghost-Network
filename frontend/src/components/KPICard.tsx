interface KPICardProps {
  label: string
  value: string | number
  description: string
  accentColor?: "blue" | "red" | "green"
  subStats?: { label: string; value: string; color?: "red" | "green" | "gray" }[]
}

export default function KPICard({ label, value, description, accentColor = "blue", subStats }: KPICardProps) {
 const colorClasses = {
  blue: "text-emerald-600",
  red: "text-red-600",
  green: "text-emerald-600",
}

  const subStatColors = {
    red: "text-red-600",
    green: "text-green-600",
    gray: "text-gray-500",
  }

  return (
   <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-6">
      <p className="text-sm font-medium text-gray-500">{label}</p>
      <p className={`text-4xl font-bold mt-2 ${colorClasses[accentColor]}`}>
        {value}
      </p>
      <p className="text-sm text-gray-400 mt-2">{description}</p>

      {subStats && subStats.length > 0 && (
        <div className="flex gap-4 mt-3 pt-3 border-t border-gray-100">
          {subStats.map((stat, i) => (
            <div key={i} className="text-xs">
              <span className={`font-semibold ${subStatColors[stat.color ?? "gray"]}`}>
                {stat.value}
              </span>{" "}
              <span className="text-gray-400">{stat.label}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}