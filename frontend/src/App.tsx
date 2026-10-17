import { useState, useEffect } from 'react'
import { C1Chat, ThemeProvider } from '@thesysai/genui-sdk'
import '@crayonai/react-ui/styles/index.css'
import '@crayonai/react-ui/styles/shell.css'
import './App.css'

interface HealthState {
  status: 'online' | 'offline' | 'checking'
  apiKeyConfigured: boolean
}

const SAMPLE_PROMPTS = [
  { label: '📈 Compare NVDA & AMD', prompt: 'Compare Nvidia (NVDA) and AMD stock price performance and valuation metrics.' },
  { label: '📊 Apple Balance Sheet', prompt: 'Visualize the latest balance sheet statement of Apple (AAPL).' },
  { label: '📉 Tesla 6-Month Trend', prompt: 'Plot the historical closing stock price of Tesla (TSLA) over the past 6 months.' },
  { label: '📰 Microsoft News', prompt: 'Retrieve the latest market news and analyst headlines for Microsoft (MSFT).' },
  { label: '🏢 Amazon Overview', prompt: 'Give me a company profile, market cap, and valuation overview for Amazon (AMZN).' },
]

function App() {
  const [health, setHealth] = useState<HealthState>({
    status: 'checking',
    apiKeyConfigured: false,
  })
  const [copiedNotice, setCopiedNotice] = useState<string | null>(null)

  useEffect(() => {
    const checkServerHealth = async () => {
      try {
        const response = await fetch('/api/health')
        if (response.ok) {
          const data = await response.json()
          setHealth({
            status: 'online',
            apiKeyConfigured: Boolean(data.api_key_configured),
          })
        } else {
          setHealth({ status: 'offline', apiKeyConfigured: false })
        }
      } catch {
        setHealth({ status: 'offline', apiKeyConfigured: false })
      }
    }

    checkServerHealth()
    const interval = setInterval(checkServerHealth, 15000)
    return () => clearInterval(interval)
  }, [])

  const handlePromptClick = (text: string) => {
    const textarea = document.querySelector('textarea.crayon-shell-thread-composer__input') as HTMLTextAreaElement | null
    if (textarea) {
      const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value')?.set
      nativeSetter?.call(textarea, text)
      textarea.dispatchEvent(new Event('input', { bubbles: true }))
      textarea.focus()
      setCopiedNotice('Prompt inserted into chat box! Press Enter to send.')
    } else {
      navigator.clipboard.writeText(text)
      setCopiedNotice('Copied prompt to clipboard! Paste it into chat below.')
    }
    setTimeout(() => setCopiedNotice(null), 3000)
  }

  return (
    <div className="finsight-wrapper">
      {/* Top Application Header */}
      <header className="finsight-header">
        <div className="header-brand">
          <div className="brand-icon-wrapper">
            <svg
              className="brand-icon"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <polyline points="22 7 13.5 15.5 8.5 10.5 2 17" />
              <polyline points="16 7 22 7 22 13" />
            </svg>
          </div>
          <div>
            <div className="brand-title-row">
              <h1 className="brand-title">FinSight AI</h1>
              <span className="brand-badge">Stock Intelligence</span>
            </div>
            <p className="brand-subtitle">Interactive Generative UI Financial Analyst</p>
          </div>
        </div>

        <div className="header-status-area">
          <div
            className={`status-pill ${
              health.status === 'online' ? 'status-online' : 'status-offline'
            }`}
          >
            <span className="status-dot"></span>
            <span>
              {health.status === 'online'
                ? health.apiKeyConfigured
                  ? 'System Ready'
                  : 'API Key Missing'
                : 'Backend Offline'}
            </span>
          </div>

          <div className="model-pill">
            <span className="model-label">Engine:</span>
            <span className="model-value">Thesys C1 • GPT-5</span>
          </div>
        </div>
      </header>

      {/* Quick Prompt Suggestions */}
      <div className="quick-prompts-bar">
        <span className="prompts-heading">Quick Inquiries:</span>
        <div className="prompts-list">
          {SAMPLE_PROMPTS.map((item, index) => (
            <button
              key={index}
              className="prompt-chip"
              onClick={() => handlePromptClick(item.prompt)}
              title="Click to insert prompt into chat"
            >
              {item.label}
            </button>
          ))}
        </div>
        {copiedNotice && (
          <div className="copied-toast">
            ✓ {copiedNotice}
          </div>
        )}
      </div>

      {/* Main Generative UI Chat Body */}
      <main className="finsight-chat-container">
        <ThemeProvider mode="dark">
          <C1Chat
            apiUrl="/api/chat"
            agentName="FinSight AI"
          />
        </ThemeProvider>
      </main>
    </div>
  )
}

export default App
