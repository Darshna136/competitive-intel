import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getCompetitorIntel } from '../api'
import ThreatBadge from '../components/ThreatBadge'
import { ArrowLeft, Target, Zap, Eye, CheckCircle } from 'lucide-react'

export default function CompetitorDetail() {
  const { name } = useParams()
  const navigate = useNavigate()
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (name) fetchData(name)
  }, [name])

  const fetchData = async (companyName: string) => {
    try {
      const res = await getCompetitorIntel(companyName)
      setData(res.data)
    } catch (err) {
      console.error('Failed to fetch competitor:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return (
    <div className="min-h-screen bg-[#0a0a0f] flex items-center justify-center">
      <div className="text-center">
        <div className="w-8 h-8 border-2 border-red-500 border-t-transparent 
                        rounded-full animate-spin mx-auto mb-4" />
        <p className="text-gray-400">Loading intelligence...</p>
      </div>
    </div>
  )

  if (!data?.brief) return (
    <div className="min-h-screen bg-[#0a0a0f] flex items-center justify-center">
      <div className="text-center">
        <p className="text-gray-400 text-lg">No intelligence available</p>
        <p className="text-gray-600 text-sm mt-2">
          Generate a briefing first from the War Room
        </p>
        <button
          onClick={() => navigate('/')}
          className="mt-4 text-red-400 hover:text-red-300"
        >
          ← Back to War Room
        </button>
      </div>
    </div>
  )

  const { company, brief } = data

  return (
    <div className="min-h-screen bg-[#0a0a0f] p-6 max-w-5xl mx-auto">
      <button
        onClick={() => navigate('/')}
        className="flex items-center gap-2 text-gray-400 hover:text-white mb-6 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to War Room
      </button>

      <div className="bg-[#12121a] border border-gray-800 rounded-xl p-6 mb-6">
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 bg-red-500/20 rounded-lg flex items-center justify-center">
                <Target className="w-6 h-6 text-red-400" />
              </div>
              <h1 className="text-3xl font-bold text-white">{brief.competitor}</h1>
            </div>
            <p className="text-gray-400">{company?.description}</p>
            <div className="flex items-center gap-3 mt-3">
              <ThreatBadge level={brief.overall_threat_level} score={brief.overall_threat_score} />
              <span className="text-gray-500 text-sm">{company?.industry}</span>
              <a href={`https://${company?.website}`} target="_blank"
                rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300 text-sm">
                {company?.website} ↗
              </a>
            </div>
          </div>
          <div className="text-center">
            <div className={`w-20 h-20 rounded-full border-4 flex items-center justify-center ${
              brief.overall_threat_score >= 75 ? 'border-red-500 bg-red-500/10' :
              brief.overall_threat_score >= 50 ? 'border-yellow-500 bg-yellow-500/10' :
              'border-green-500 bg-green-500/10'
            }`}>
              <span className="text-2xl font-bold text-white">{brief.overall_threat_score}</span>
            </div>
            <p className="text-gray-500 text-xs mt-1">Threat Score</p>
          </div>
        </div>
        <div className="mt-5 pt-5 border-t border-gray-800">
          <h3 className="text-gray-400 text-sm font-medium uppercase tracking-wider mb-2">
            Executive Summary
          </h3>
          <p className="text-gray-300 leading-relaxed">{brief.executive_summary}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-[#12121a] border border-red-500/20 rounded-xl p-5">
          <h3 className="text-red-400 font-semibold mb-3 flex items-center gap-2">
            <Zap className="w-4 h-4" /> Top Risks
          </h3>
          {brief.top_3_risks?.map((risk: string, i: number) => (
            <div key={i} className="flex items-start gap-2 mb-2">
              <span className="text-red-500 mt-0.5">⚠</span>
              <p className="text-gray-400 text-sm">{risk}</p>
            </div>
          ))}
        </div>

        <div className="bg-[#12121a] border border-purple-500/20 rounded-xl p-5">
          <h3 className="text-purple-400 font-semibold mb-3 flex items-center gap-2">
            <Eye className="w-4 h-4" /> Predicted Moves
          </h3>
          {brief.predicted_moves?.map((move: string, i: number) => (
            <div key={i} className="flex items-start gap-2 mb-2">
              <span className="text-purple-500 mt-0.5">🔮</span>
              <p className="text-gray-400 text-sm">{move}</p>
            </div>
          ))}
        </div>

        <div className="bg-[#12121a] border border-green-500/20 rounded-xl p-5">
          <h3 className="text-green-400 font-semibold mb-3 flex items-center gap-2">
            <CheckCircle className="w-4 h-4" /> Actions Required
          </h3>
          {brief.recommended_actions?.map((action: string, i: number) => (
            <div key={i} className="flex items-start gap-2 mb-2">
              <span className="text-green-500 mt-0.5">✓</span>
              <p className="text-gray-400 text-sm">{action}</p>
            </div>
          ))}
        </div>
      </div>

      {brief.convergence_signals?.length > 0 && (
        <div className="bg-[#12121a] border border-yellow-500/20 rounded-xl p-5">
          <h3 className="text-yellow-400 font-semibold mb-4">🎯 Signal Convergence</h3>
          {brief.convergence_signals.map((signal: any, i: number) => (
            <div key={i} className="bg-yellow-500/5 border border-yellow-500/10 rounded-lg p-4 mb-3">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-white font-medium text-sm">{signal.finding}</p>
                  <p className="text-gray-400 text-sm mt-1">{signal.implication}</p>
                </div>
                <ThreatBadge level={signal.confidence} />
              </div>
              <div className="flex gap-2 mt-2 flex-wrap">
                {signal.sources?.map((src: string) => (
                  <span key={src} className="text-xs bg-gray-800 text-gray-400 px-2 py-0.5 rounded">
                    {src}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}