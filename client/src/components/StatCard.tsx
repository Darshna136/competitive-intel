interface Props {
  title: string
  value: string | number
  subtitle?: string
  color?: string
}

export default function StatCard({ title, value, subtitle, color = "blue" }: Props) {
  const colors: Record<string, string> = {
    blue:   "from-blue-500/10 to-blue-600/5 border-blue-500/20",
    red:    "from-red-500/10 to-red-600/5 border-red-500/20",
    green:  "from-green-500/10 to-green-600/5 border-green-500/20",
    yellow: "from-yellow-500/10 to-yellow-600/5 border-yellow-500/20"
  }

  return (
    <div className={`bg-gradient-to-br ${colors[color]} border rounded-xl p-5`}>
      <p className="text-gray-400 text-sm font-medium">{title}</p>
      <p className="text-3xl font-bold text-white mt-1">{value}</p>
      {subtitle && <p className="text-gray-500 text-xs mt-1">{subtitle}</p>}
    </div>
  )
}