interface Props {
  level: string
  score?: number
}

export default function ThreatBadge({ level, score }: Props) {
  const colors: Record<string, string> = {
    HIGH:    "bg-red-500/20 text-red-400 border border-red-500/30",
    MEDIUM:  "bg-yellow-500/20 text-yellow-400 border border-yellow-500/30",
    LOW:     "bg-green-500/20 text-green-400 border border-green-500/30",
    UNKNOWN: "bg-gray-500/20 text-gray-400 border border-gray-500/30"
  }

  const dots: Record<string, string> = {
    HIGH: "bg-red-400", MEDIUM: "bg-yellow-400",
    LOW: "bg-green-400", UNKNOWN: "bg-gray-400"
  }

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold ${colors[level] || colors.UNKNOWN}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${dots[level] || dots.UNKNOWN} animate-pulse`} />
      {level} {score !== undefined && `(${score}/100)`}
    </span>
  )
}