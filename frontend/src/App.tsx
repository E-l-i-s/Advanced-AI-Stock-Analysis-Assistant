import { useState } from 'react'
import { C1Chat, ThemeProvider } from '@thesysai/genui-sdk'
import '@crayonai/react-ui/styles/index.css'
import '@crayonai/react-ui/styles/shell.css'
import '@thesysai/genui-sdk/dist/genui-sdk.css'
import './App.css'

const SAMPLE_PROMPTS = [
  { label: '📈 Compare NVDA & AMD', prompt: 'Compare Nvidia (NVDA) and AMD stock price performance and valuation metrics.' },
  { label: '📊 Apple Balance Sheet', prompt: 'Visualize the latest balance sheet statement of Apple (AAPL).' },
  { label: '📉 Tesla 6-Month Trend', prompt: 'Plot the historical closing stock price of Tesla (TSLA) over the past 6 months.' },
  { label: '📰 Microsoft News', prompt: 'Retrieve the latest market news and analyst headlines for Microsoft (MSFT).' },
  { label: '🏢 Amazon Overview', prompt: 'Give me a company profile, market cap, and valuation overview for Amazon (AMZN).' },
]

function App() {
  const [copiedNotice, setCopiedNotice] = useState<string | null>(null)

  const handlePromptClick = (text: string) => {
    const textarea = document.querySelector('textarea.crayon-shell-thread-composer__input') as HTMLTextAreaElement | null
    if (textarea) {
      const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value')?.set
      nativeSetter?.call(textarea, text)
      textarea.dispatchEvent(new Event('input', { bubbles: true }))
      textarea.focus()
      setCopiedNotice('Prompt inserted — press Enter to send.')
    } else {
      navigator.clipboard.writeText(text)
      setCopiedNotice('Copied to clipboard!')
    }
    setTimeout(() => setCopiedNotice(null), 3000)
  }

  return (
    <div className="app-wrapper">
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

      {/* Generative UI Chat */}
      <main className="chat-container">
        <ThemeProvider mode="dark">
          <C1Chat
            apiUrl="/api/chat"
            agentName="Stock Analysis Assistant"
          />
        </ThemeProvider>
      </main>
    </div>
  )
}

export default App
