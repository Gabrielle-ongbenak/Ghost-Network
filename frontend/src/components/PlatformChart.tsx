import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from "recharts"

interface PlatformData {
  platform: string
  count: number
  percentage: number
  riskLevel: "high" | "medium" | "low"
}

interface PlatformChartProps {
  data: PlatformData[]
}

const platformColors = ["#059669", "#f97316", "#0d9488", "#a855f7"]

export default function PlatformChart({ data }: PlatformChartProps) {
  const total = data.reduce((sum, item) => sum + item.count, 0)

  return (
   <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-6">
      <h2 className="text-lg font-bold text-gray-900">Listings by Platform</h2>
      <p className="text-sm text-gray-500 mt-1 mb-4">
        Where these suspicious job ads are being posted.
      </p>

      <div className="flex items-center gap-6">
        <ResponsiveContainer width="100%" height={200}>
          <PieChart>
            <Pie
              data={data}
              dataKey="count"
              nameKey="platform"
              innerRadius={55}
              outerRadius={80}
              paddingAngle={2}
            >
              {data.map((_, index) => (
                <Cell key={index} fill={platformColors[index % platformColors.length]} />
              ))}
            </Pie>
            <Tooltip formatter={(value) => `${value} listings`} />
          </PieChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-2 space-y-2">
        {data.map((item, index) => (
          <div key={item.platform} className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-2">
              <span
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: platformColors[index % platformColors.length] }}
              />
              <span className="text-gray-700">{item.platform}</span>
            </div>
            <span className="text-gray-500">
              {item.count} ({item.percentage}%)
            </span>
          </div>
        ))}
      </div>

      <p className="text-xs text-gray-400 mt-3">Total flagged: {total} listings</p>
    </div>
  )
}