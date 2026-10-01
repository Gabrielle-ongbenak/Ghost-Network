import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts"
import type { CountryBreakdown } from "../types/listing"

interface CountryChartProps {
  data: CountryBreakdown[]
}

const barColors = ["#059669", "#f97316", "#0d9488"]

export default function CountryChart({ data }: CountryChartProps) {
  return (
   <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-6">
      <h2 className="text-lg font-bold text-gray-900">Where are the scams happening?</h2>
      <p className="text-sm text-gray-500 mt-1 mb-4">
        Scam frequency across our 3 monitored regions and the typical trick used.
      </p>

      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={data} layout="vertical" margin={{ left: 20 }}>
          <XAxis type="number" hide />
          <YAxis
            type="category"
            dataKey="countryName"
            width={90}
            tick={{ fontSize: 13, fill: "#374151" }}
            axisLine={false}
            tickLine={false}
            />
          
                      <Tooltip
            formatter={(value) => `${value} listings flagged`}
          />
          <Bar dataKey="flaggedCount" radius={[0, 8, 8, 0]} barSize={24}>
            {data.map((_, index) => (
              <Cell key={index} fill={barColors[index % barColors.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      <div className="mt-4 space-y-2">
        {data.map((country) => (
          <p key={country.country} className="text-sm text-gray-500">
            <span className="font-semibold text-gray-700">{country.countryName}:</span>{" "}
            {country.insight}
          </p>
        ))}
      </div>
    </div>
  )
}