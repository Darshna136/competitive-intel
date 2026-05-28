import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getStats, getLatestBriefing, generateBriefing } from '../api'

const COLORS = {
  HIGH:    '#ef4444',
  MEDIUM:  '#f59e0b',
  LOW:     '#10b981',
  UNKNOWN: '#6b7280',
}

const BG = {
  HIGH:    'rgba(239,68,68,0.06)',
  MEDIUM:  'rgba(245,158,11,0.06)',
  LOW:     'rgba(16,185,129,0.06)',
  UNKNOWN: 'rgba(107,114,128,0.06)',
}

export default function WarRoom() {
  const [stats, setStats] = useState<any>(null)
  const [briefs, setBriefs] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [lastUpdated, setLastUpdated] = useState('')
  const [time, setTime] = useState(new Date())
  const [activeCard, setActiveCard] = useState<number | null>(null)
  const navigate = useNavigate()

  useEffect(() => {
    fetchData()
    const t = setInterval(() => setTime(new Date()), 1000)
    return () => clearInterval(t)
  }, [])

  const fetchData = async () => {
    try {
      const [s, b] = await Promise.all([getStats(), getLatestBriefing()])
      setStats(s.data)
      if (b.data.company_briefs) {
        setBriefs([...b.data.company_briefs].sort((a, b) => (b.overall_threat_score || 0) - (a.overall_threat_score || 0)))
        setLastUpdated(b.data.generated_at || '')
      }
    } catch (e) { console.error(e) }
  }

  const handleGenerate = async () => {
    setLoading(true)
    try {
      const res = await generateBriefing()
      setBriefs([...res.data.company_briefs].sort((a, b) => (b.overall_threat_score || 0) - (a.overall_threat_score || 0)))
      setLastUpdated(res.data.generated_at || '')
      await fetchData()
    } catch (e) { console.error(e) }
    finally { setLoading(false) }
  }

  const high = briefs.filter(b => b.overall_threat_level === 'HIGH').length

  return (
    <div style={{ minHeight: '100vh', background: '#050510', color: '#fff', fontFamily: "'Space Grotesk', sans-serif", overflow: 'hidden' }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap');
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }
        @keyframes slideUp { from{opacity:0;transform:translateY(20px)} to{opacity:1;transform:translateY(0)} }
        @keyframes spin { to{transform:rotate(360deg)} }
        @keyframes scanline { 0%{transform:translateY(-100%)} 100%{transform:translateY(100vh)} }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        ::-webkit-scrollbar { width: 3px; }
        ::-webkit-scrollbar-thumb { background: rgba(239,68,68,0.4); border-radius: 2px; }
        .card-hover { transition: all 0.3s cubic-bezier(0.4,0,0.2,1); }
        .card-hover:hover { transform: translateY(-4px); }
        .btn-glow:hover { box-shadow: 0 0 24px rgba(239,68,68,0.4); }
      `}</style>

      {/* Ambient background blobs */}
      <div style={{ position: 'fixed', inset: 0, pointerEvents: 'none', zIndex: 0 }}>
        <div style={{ position: 'absolute', top: '-20%', right: '-10%', width: '600px', height: '600px', borderRadius: '50%', background: 'radial-gradient(circle, rgba(239,68,68,0.08) 0%, transparent 70%)' }} />
        <div style={{ position: 'absolute', bottom: '-20%', left: '-10%', width: '500px', height: '500px', borderRadius: '50%', background: 'radial-gradient(circle, rgba(99,102,241,0.06) 0%, transparent 70%)' }} />
        <div style={{ position: 'absolute', top: '40%', left: '30%', width: '400px', height: '400px', borderRadius: '50%', background: 'radial-gradient(circle, rgba(245,158,11,0.04) 0%, transparent 70%)' }} />
      </div>

      {/* Navbar */}
      <nav style={{ position: 'fixed', top: 0, left: 0, right: 0, zIndex: 100, padding: '0 40px', height: '64px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: 'rgba(5,5,16,0.8)', backdropFilter: 'blur(20px)', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ width: '32px', height: '32px', borderRadius: '8px', background: 'linear-gradient(135deg, #ef4444, #ed1a1a)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '14px', fontWeight: '700' }}>W</div>
          <span style={{ fontFamily: "'Space Grotesk', sans-serif", fontWeight: '700', fontSize: '16px', letterSpacing: '0.5px' }}>WarRoom</span>
          <span style={{ fontSize: '11px', color: 'rgba(255,255,255,0.3)', background: 'rgba(255,255,255,0.06)', padding: '2px 8px', borderRadius: '4px', letterSpacing: '1px' }}>BETA</span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', color: 'rgba(255,255,255,0.3)', fontFamily: 'monospace' }}>
          <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#10b981', animation: 'pulse 2s infinite' }} />
          {time.toLocaleTimeString('en-US', { hour12: false })} UTC
        </div>

        <button onClick={handleGenerate} disabled={loading} className="btn-glow" style={{ display: 'flex', alignItems: 'center', gap: '8px', background: loading ? 'rgba(239,68,68,0.1)' : 'rgba(239,68,68,0.15)', border: '1px solid rgba(239,68,68,0.3)', color: '#ef4444', padding: '10px 20px', borderRadius: '10px', fontSize: '13px', fontWeight: '500', cursor: loading ? 'not-allowed' : 'pointer', transition: 'all 0.2s', fontFamily: "'Space Grotesk', sans-serif" }}>
          {loading
            ? <><div style={{ width: '14px', height: '14px', border: '2px solid rgba(239,68,68,0.3)', borderTop: '2px solid #ef4444', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} /> Running agents...</>
            : <><span style={{ fontSize: '16px' }}>⚡</span> Run Intelligence Sweep</>
          }
        </button>
      </nav>

      <div style={{ position: 'relative', zIndex: 1, paddingTop: '64px' }}>

        {/* Hero Section */}
        <div style={{ padding: '80px 40px 48px', maxWidth: '1400px', margin: '0 auto', animation: 'slideUp 0.6s ease' }}>
          <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', flexWrap: 'wrap', gap: '32px' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
                <div style={{ height: '1px', width: '32px', background: '#ef4444' }} />
                <span style={{ fontSize: '11px', letterSpacing: '3px', color: '#ef4444', textTransform: 'uppercase' }}>Live Intelligence</span>
              </div>
              <h1 style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: '64px', fontWeight: '800', lineHeight: '1.0', letterSpacing: '-2px', marginBottom: '16px' }}>
                Competitive<br />
                <span style={{  fontFamily: "'Space Grotesk', sans-serif", fontSize: '64px', fontWeight: '800', lineHeight: '1.0', letterSpacing: '-2px', marginBottom: '16px'}}>War Room</span>
              </h1>
              <p style={{ color: 'rgba(255, 255, 255, 0.8)', fontSize: '15px', maxWidth: '480px', lineHeight: '1.7' }}>
                5 autonomous AI agents monitor your competitors 24/7 — news, code activity, hiring, pricing — synthesized into actionable intelligence.
              </p>
            </div>

            {/* Live Stats */}
            {stats && (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px', minWidth: '320px' }}>
                {[
                  { label: 'Targets', value: stats.total_competitors, color: '#60a5fa' },
                  { label: 'High Threat', value: stats.high_threats, color: '#ef4444' },
                  { label: 'Avg Score', value: `${Math.round(stats.average_threat_score)}`, color: '#f59e0b' },
                  { label: 'Agents', value: stats.agents_running, color: '#10b981' },
                ].map(({ label, value, color }) => (
                  <div key={label} style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.07)', borderRadius: '16px', padding: '20px', textAlign: 'center' }}>
                    <div style={{ fontSize: '36px', fontFamily: "'Space Grotesk', sans-serif", fontWeight: '800', color, lineHeight: 1 }}>{value}</div>
                    <div style={{ fontSize: '11px', color: 'rgba(255,255,255,0.3)', marginTop: '6px', letterSpacing: '1px', textTransform: 'uppercase' }}>{label}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Divider with last updated */}
        {lastUpdated && (
          <div style={{ padding: '0 40px', maxWidth: '1400px', margin: '0 auto 40px', display: 'flex', alignItems: 'center', gap: '16px' }}>
            <div style={{ flex: 1, height: '1px', background: 'rgba(255,255,255,0.06)' }} />
            <span style={{ fontSize: '11px', color: 'rgba(255,255,255,0.2)', letterSpacing: '1px', whiteSpace: 'nowrap' }}>
              LAST SWEEP · {new Date(lastUpdated).toLocaleString().toUpperCase()}
            </span>
            <div style={{ flex: 1, height: '1px', background: 'rgba(255,255,255,0.06)' }} />
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div style={{ margin: '0 40px 40px', maxWidth: '1400px', marginLeft: 'auto', marginRight: 'auto', background: 'rgba(239,68,68,0.05)', border: '1px solid rgba(239,68,68,0.15)', borderRadius: '16px', padding: '20px 28px', display: 'flex', alignItems: 'center', gap: '16px' }}>
            <div style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#ef4444', animation: 'pulse 1s infinite' }} />
            <div>
              <div style={{ fontSize: '14px', fontWeight: '500', color: '#ef4444' }}>Intelligence sweep in progress</div>
              <div style={{ fontSize: '12px', color: 'rgba(255,255,255,0.3)', marginTop: '4px' }}>News Hawk → GitHub Watcher → Job Spy → Price Watcher → Synthesizer</div>
            </div>
          </div>
        )}

        {/* Threat Cards */}
        {briefs.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '100px 40px' }}>
            <div style={{ fontSize: '64px', opacity: 0.1, marginBottom: '24px' }}>◎</div>
            <div style={{ fontSize: '16px', color: 'rgba(255,255,255,0.2)', letterSpacing: '2px' }}>NO DATA — RUN AN INTELLIGENCE SWEEP</div>
          </div>
        ) : (
          <div style={{ padding: '0 40px 80px', maxWidth: '1400px', margin: '0 auto' }}>

            {/* Featured Card — Top Threat */}
            {briefs[0] && (() => {
              const b = briefs[0]
              const level = b.overall_threat_level || 'UNKNOWN'
              const color = COLORS[level as keyof typeof COLORS] || COLORS.UNKNOWN
              const score = b.overall_threat_score || 0
              return (
                <div onClick={() => navigate(`/competitor/${b.competitor}`)} className="card-hover" style={{ background: `linear-gradient(135deg, ${BG[level as keyof typeof BG]} 0%, rgba(255,255,255,0.02) 100%)`, border: `1px solid ${color}30`, borderRadius: '24px', padding: '40px', marginBottom: '20px', cursor: 'pointer', position: 'relative', overflow: 'hidden', animation: 'slideUp 0.4s ease' }}>
                  <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: '3px', background: `linear-gradient(90deg, ${color}, transparent)` }} />
                  <div style={{ position: 'absolute', top: '40px', right: '40px', fontSize: '100px', fontFamily: "'Space Grotesk', sans-serif", fontWeight: '800', color: `${color}08`, lineHeight: 1, pointerEvents: 'none' }}>{score}</div>

                  <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '24px' }}>
                    <div>
                      <div style={{ fontSize: '11px', letterSpacing: '3px', color: 'rgba(255,255,255,0.3)', marginBottom: '10px', textTransform: 'uppercase' }}>⚡ Top Threat</div>
                      <div style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: '42px', fontWeight: '800', letterSpacing: '-1px', color }}>{b.competitor}</div>
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', alignItems: 'flex-end' }}>
                      <span style={{ fontSize: '11px', padding: '6px 14px', borderRadius: '100px', background: `${color}20`, color, border: `1px solid ${color}40`, letterSpacing: '1px', fontWeight: '500' }}>{level}</span>
                      {b.urgency && <span style={{ fontSize: '11px', padding: '6px 14px', borderRadius: '100px', background: 'rgba(255,255,255,0.05)', color: 'rgba(255,255,255,0.5)', letterSpacing: '1px' }}>{b.urgency}</span>}
                    </div>
                  </div>

                  <div style={{ marginBottom: '24px' }}>
                    <div style={{ height: '4px', background: 'rgba(255,255,255,0.06)', borderRadius: '2px', overflow: 'hidden' }}>
                      <div style={{ height: '100%', width: `${score}%`, background: `linear-gradient(90deg, ${color}80, ${color})`, borderRadius: '2px', transition: 'width 1.5s ease' }} />
                    </div>
                  </div>

                  <p style={{ fontSize: '14px', color: 'rgba(255,255,255,0.5)', lineHeight: '1.8', maxWidth: '700px', marginBottom: '28px' }}>{b.executive_summary}</p>

                  <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
                    {b.convergence_signals?.slice(0, 2).map((s: any, i: number) => (
                      <div key={i} style={{ fontSize: '12px', background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '8px', padding: '8px 14px', color: 'rgba(255,255,255,0.4)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{ color }}>●</span> {s.finding?.slice(0, 60)}{s.finding?.length > 60 ? '...' : ''}
                      </div>
                    ))}
                    <div style={{ fontSize: '12px', color: 'rgba(255,255,255,0.2)', padding: '8px 14px', display: 'flex', alignItems: 'center', gap: '4px' }}>View full intel →</div>
                  </div>
                </div>
              )
            })()}

            {/* Grid — Remaining Cards */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: '16px' }}>
              {briefs.slice(1).map((b, i) => {
                const level = b.overall_threat_level || 'UNKNOWN'
                const color = COLORS[level as keyof typeof COLORS] || COLORS.UNKNOWN
                const score = b.overall_threat_score || 0
                const isActive = activeCard === i

                return (
                  <div key={b.competitor}
                    onClick={() => navigate(`/competitor/${b.competitor}`)}
                    onMouseEnter={() => setActiveCard(i)}
                    onMouseLeave={() => setActiveCard(null)}
                    className="card-hover"
                    style={{
                      background: isActive ? BG[level as keyof typeof BG] : 'rgba(255,255,255,0.02)',
                      border: `1px solid ${isActive ? `${color}30` : 'rgba(255,255,255,0.06)'}`,
                      borderRadius: '20px', padding: '28px',
                      cursor: 'pointer', position: 'relative', overflow: 'hidden',
                      animation: `slideUp 0.4s ease ${i * 0.08}s both`,
                    }}>

                    <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: '2px', background: isActive ? `linear-gradient(90deg, ${color}, transparent)` : 'transparent', transition: 'all 0.3s' }} />

                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px' }}>
                      <div>
                        <div style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: '22px', fontWeight: '800', color: isActive ? color : '#fff', transition: 'color 0.3s', marginBottom: '6px' }}>{b.competitor}</div>
                        <span style={{ fontSize: '11px', padding: '3px 10px', borderRadius: '100px', background: `${color}15`, color, border: `1px solid ${color}30`, letterSpacing: '1px' }}>{level}</span>
                      </div>
                      <div style={{ textAlign: 'right' }}>
                        <div style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: '32px', fontWeight: '800', color: `${color}60`, lineHeight: 1 }}>{score}</div>
                        <div style={{ fontSize: '10px', color: 'rgba(255,255,255,0.2)', letterSpacing: '1px' }}>/ 100</div>
                      </div>
                    </div>

                    <div style={{ height: '2px', background: 'rgba(255,255,255,0.05)', borderRadius: '1px', overflow: 'hidden', marginBottom: '20px' }}>
                      <div style={{ height: '100%', width: `${score}%`, background: color, borderRadius: '1px' }} />
                    </div>

                    <p style={{ fontSize: '13px', color: 'rgba(255,255,255,0.4)', lineHeight: '1.7', marginBottom: '20px', display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                      {b.executive_summary}
                    </p>

                    <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                      {b.top_3_risks?.slice(0, 2).map((r: string, j: number) => (
                        <div key={j} style={{ fontSize: '11px', background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: '6px', padding: '4px 10px', color: 'rgba(255,255,255,0.3)' }}>
                          ▸ {r.slice(0, 40)}{r.length > 40 ? '...' : ''}
                        </div>
                      ))}
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {/* Footer */}
        <div style={{ borderTop: '1px solid rgba(255,255,255,0.04)', padding: '24px 40px', display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: 'rgba(255,255,255,0.15)', letterSpacing: '1px' }}>
          <span>WARROOM — MULTI-AGENT AI SYSTEM</span>
          <span>GROQ × LANGGRAPH × TAVILY × GITHUB</span>
        </div>
      </div>
    </div>
  )
}