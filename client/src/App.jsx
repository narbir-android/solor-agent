import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [report, setReport] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [lastCheck, setLastCheck] = useState(null)

  const fetchLatest = async () => {
    try {
      const res = await fetch('http://localhost:5000/api/latest-report')
      const data = await res.json()
      if (data.report) {
        setReport(data.report)
        setLastCheck(data.date)
        setError(null)
      } else if (data.error) {
        setError("No reports found yet.")
      }
    } catch (err) {
      console.error(err)
      setError("Server disconnected. Start the server folder with 'node index.js'")
    }
  }

  const runManual = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch('http://localhost:5000/api/run-agent', { method: 'POST' })
      const data = await res.json()
      if (data.report) {
        setReport(data.report)
        setLastCheck(new Date().toLocaleTimeString())
      }
    } catch (err) {
      setError("Failed to trigger agent. Check server status.")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchLatest()
    const interval = setInterval(fetchLatest, 30000) // Poll every 30s
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="App">
      <header>
        <div className="status-badge status-live">Live Intelligence</div>
        <h1>Solar Agent Pro</h1>
        <p className="subtitle">Real-time US market intelligence and competitor analysis.</p>
        <button onClick={runManual} disabled={loading}>
          {loading ? "Analyzing Market..." : "Force Real-time Scan"}
        </button>
      </header>

      {error && <div className="card" style={{borderColor: '#ef4444', color: '#ef4444'}}>{error}</div>}

      <main className="card">
        <div className="report-header">
           <div style={{fontWeight: 600, color: '#fbbf24', display: 'flex', alignItems: 'center'}}>
             <span style={{marginRight: '8px'}}>⚡</span> Latest Market Intelligence
           </div>
           <div style={{fontSize: '0.85rem', color: '#64748b'}}>
             Last sync: {lastCheck || 'Never'}
           </div>
        </div>

        {loading ? (
          <div style={{textAlign: 'center', padding: '4rem'}}>
            <div className="loading-spinner"></div>
            <p style={{color: '#94a3b8', marginTop: '1rem'}}>Aggregating news and competitor data...</p>
          </div>
        ) : report ? (
          <div className="report-container">
            {report.split('\n').map((line, i) => (
              <p key={i} style={{
                color: line.startsWith('###') ? '#fbbf24' : '#e2e8f0',
                fontWeight: line.startsWith('###') ? '700' : '400',
                fontSize: line.startsWith('###') ? '1.4rem' : '1rem',
                marginTop: line.startsWith('###') ? '2rem' : '0.5rem',
                borderLeft: line.startsWith('-') ? '2px solid rgba(251, 191, 36, 0.3)' : 'none',
                paddingLeft: line.startsWith('-') ? '1rem' : '0'
              }}>
                {line.replace(/###/g, '')}
              </p>
            ))}
          </div>
        ) : (
          <div style={{textAlign: 'center', padding: '4rem', color: '#475569'}}>
             Scan required. Click the button above to generate your first intelligence report.
          </div>
        )}
      </main>

      <footer style={{marginTop: '4rem', fontSize: '0.8rem', color: '#475569'}}>
        &copy; 2026 Solar Agent Dashboard &bull; Powered by Gemini 2.5 Flash
      </footer>
    </div>
  )
}

export default App
