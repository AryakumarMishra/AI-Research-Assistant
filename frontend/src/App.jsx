import { useState } from 'react'
import Header from './components/Header'
import ChatPanel from './components/ChatPanel'
import Sidebar from './components/Sidebar'
import './App.css'

function App() {
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [sources, setSources] = useState([])
  const [findings, setFindings] = useState([])
  const [showSidebar, setShowSidebar] = useState(true)

  const handleSendMessage = async (content) => {
    const userMessage = { role: 'user', content, timestamp: new Date() }
    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: content })
      })

      const data = await response.json()
      
      const assistantMessage = { 
        role: 'assistant', 
        content: data.response, 
        timestamp: new Date() 
      }
      
      setMessages(prev => [...prev, assistantMessage])
      
      if (data.sources?.length > 0) {
        setSources(prev => [...prev, ...data.sources])
      }
      
      if (data.findings?.length > 0) {
        setFindings(data.findings)
      }
    } catch (error) {
      const errorMessage = { 
        role: 'assistant', 
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
        isError: true
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const clearChat = () => {
    setMessages([])
    setSources([])
    setFindings([])
  }

  const handleExport = async () => {
    if (messages.length === 0) return

    const lastAssistantMessage = messages.findLast(m => m.role === 'assistant')
    if (!lastAssistantMessage) return

    try {
      const response = await fetch('/api/export', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic: sources.length > 0 ? 'Research Report' : 'Chat History',
          response: lastAssistantMessage.content,
          sources: sources,
          findings: findings
        })
      })

      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = 'research_report.md'
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
      }
    } catch (error) {
      console.error('Export failed:', error)
    }
  }

  return (
    <div className="app">
      <Header 
        onToggleSidebar={() => setShowSidebar(!showSidebar)}
        onClearChat={clearChat}
        onExport={handleExport}
        messageCount={messages.length}
      />
      
      <div className="main-container">
        <ChatPanel 
          messages={messages}
          isLoading={isLoading}
          onSendMessage={handleSendMessage}
        />
        
        {showSidebar && (
          <Sidebar 
            sources={sources}
            findings={findings}
          />
        )}
      </div>
    </div>
  )
}

export default App
