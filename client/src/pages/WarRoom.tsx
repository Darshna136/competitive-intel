import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getStats, getLatestBriefing, generateBriefing } from '../api'
import ThreatBadge from '../components/ThreatBadge'
import StatCard from '../components/StatCard'
import { RefreshCw, Zap, Shield, Target, Clock } from 'lucide-react'

export default function WarRoom() {
  const [stats, setStats] = useState<any>(null)
  const [briefs, setBriefs] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [lastUpdated, setLastUpdated] = useState<string>('')
  const navigate = useNavigate()

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [statsRes, briefingRes] = await Promise.all([
        getStats(),
        getLatestBriefing()
      ])
      setStats(statsRes.data)
      if (briefingRes.data.company_briefs) {
        const sorted = [...briefingRes.data.company_briefs].sort(
          (a, b) => (b.overall_threat_score || 0) - (a.overall_threat_score || 0)
        )
        setBriefs(sorted)
        setLastUpdated(briefingRes.data.generated_at || '')
      }
    } catch (err) {
      console.error('Failed to fetch data:', err)
    }
  }

  const handleGenerate = async () => {
    setLoading(true)
    try {
      const res = await generateBriefing()
      const sorted = [...res.data.company_briefs].sort(
        (a, b) => (b.overall_threat_score || 0) - (a.overall_threat_score || 0)
      )
      setBriefs(sorted)
      setLastUpdated(res.data.generated_at || '')
      await fetchData()
    } catch (err) {
      console.error('Failed to generate:', err)
    } finally {
      setLoading(false)
    }
  }

  const urgencyColor: Record<string, string> = {
    "ACT NOW":        "text-red-400 bg-red-500/10 border-red-500/20",
    "MONITOR CLOSELY":"text-yellow-400 bg-yellow-500/10 border-yellow-500/20",
    "WATCH":          "text-blue-400 bg-blue-500/10 border-blue-500/20"
  }

  return (
    <div className="min-h-screen bg-[#0a0a0f] p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <div className="w-8 h-8 bg-red-500 rounded-lg flex items-center justify-center">
              <Target className="w-5 h-5 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-white">
              Competitive Intelligence War Room
            </h1>
          </div>
          <p className="text-gray-500 text-sm ml-11">
            AI-powered competitive surveillance system
          </p>
        </div>
        <button
          onClick={handleGenerate}
          disabled={loading}
          className="flex items-center gap-2 bg-red-500 hover:bg-red-600 
                     disabled:opacity-50 text-white px-5 py-2.5 rounded-lg 
                     font-medium transition-all duration-200"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          {loading ? 'Running All Agents...' : 'Generate Fresh Briefing'}
        </button>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-xl p-4 mb-6">
          <div className="flex items-center gap-3">
            <div className="w-2 h-2 bg-yellow-400 rounded-full animate-pulse" />
            <p className="text-yellow-400 font-medium">
              Running 4 AI agents — News Hawk, GitHub Watcher, Job Spy, Price Watcher...
            </p>
          </div>
          <p className="text-gray-500 text-sm mt-1 ml-5">
            This takes 2-3 minutes. Please wait.
          </p>
        </div>
      )}

      {/* Stats Row */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <StatCard
            title="Companies Monitored"
            value={stats.total_competitors}
            subtitle="tracked 24/7"
            color="blue"
          />
          <StatCard
            title="High Threats"
            value={stats.high_threats}
            subtitle="require action"
            color="red"
          />
          <StatCard
            title="Avg Threat Score"
            value={`${stats.average_threat_score}/100`}
            subtitle="across all competitors"
            color="yellow"
          />
          <StatCard
            title="AI Agents Active"
            value={stats.agents_running}
            subtitle="running continuously"
            color="green"
          />
        </div>
      )}

      {/* Last Updated */}
      {lastUpdated && (
        <div className="flex items-center gap-2 text-gray-500 text-sm mb-6">
          <Clock className="w-4 h-4" />
          Last updated: {new Date(lastUpdated).toLocaleString()}
        </div>
      )}

      {/* Competitor Cards */}
      {briefs.length === 0 ? (
        <div className="text-center py-20">
          <Shield className="w-16 h-16 text-gray-700 mx-auto mb-4" />
          <p className="text-gray-500 text-lg">No briefing generated yet</p>
          <p className="text-gray-600 text-sm mt-2">
            Click "Generate Fresh Briefing" to run all agents
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {briefs.map((brief: any) => (
            <div
              key={brief.competitor}
              onClick={() => navigate(`/competitor/${brief.competitor}`)}
              className="bg-[#12121a] border border-gray-800 hover:border-gray-600 
                         rounded-xl p-5 cursor-pointer transition-all duration-200
                         hover:transform hover:-translate-y-1"
            >
              {/* Card Header */}
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="text-white font-bold text-lg">
                    {brief.competitor}
                  </h3>
                  <div className="flex items-center gap-2 mt-1">
                    <ThreatBadge
                      level={brief.overall_threat_level}
                      score={brief.overall_threat_score}
                    />
                  </div>
                </div>
                <span className={`text-xs px-2 py-1 rounded-lg border font-medium
                                  ${urgencyColor[brief.urgency] || 'text-gray-400'}`}>
                  {brief.urgency}
                </span>
              </div>

              {/* Threat Score Bar */}
              <div className="mb-4">
                <div className="flex justify-between text-xs text-gray-500 mb-1">
                  <span>Threat Score</span>
                  <span>{brief.overall_threat_score}/100</span>
                </div>
                <div className="w-full bg-gray-800 rounded-full h-1.5">
                  <div
                    className={`h-1.5 rounded-full transition-all duration-500 ${
                      brief.overall_threat_score >= 75 ? 'bg-red-500' :
                      brief.overall_threat_score >= 50 ? 'bg-yellow-500' : 'bg-green-500'
                    }`}
                    style={{ width: `${brief.overall_threat_score}%` }}
                  />
                </div>
              </div>

              {/* Executive Summary */}
              <p className="text-gray-400 text-sm leading-relaxed line-clamp-3 mb-4">
                {brief.executive_summary}
              </p>

              {/* Top Risks */}
              {brief.top_3_risks?.slice(0, 2).map((risk: string, i: number) => (
                <div key={i} className="flex items-start gap-2 mb-1">
                  <Zap className="w-3 h-3 text-red-400 mt-0.5 flex-shrink-0" />
                  <p className="text-gray-500 text-xs line-clamp-1">{risk}</p>
                </div>
              ))}

              {/* Click hint */}
              <p className="text-gray-700 text-xs mt-3 text-right">
                Click for full intel →
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
