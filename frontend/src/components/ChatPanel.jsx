import { Send, Sparkles } from 'lucide-react'
import { useState, useRef, useEffect } from 'react'
import MessageList from './MessageList'
import './ChatPanel.css'

function ChatPanel({ messages, isLoading, onSendMessage }) {
  const [input, setInput] = useState('')
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return
    
    onSendMessage(input.trim())
    setInput('')
  }

  const suggestions = [
    "Latest AI research on transformers",
    "Recent papers on climate change",
    "Quantum computing breakthroughs 2024"
  ]

  return (
    <div className="chat-panel">
      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="welcome-screen">
            <div className="welcome-icon">
              <Sparkles size={48} />
            </div>
            <h2 className="welcome-title">What would you like to research?</h2>
            <p className="welcome-subtitle">
              I can search the web and academic papers to help you find answers.
            </p>
            
            <div className="suggestions">
              {suggestions.map((suggestion, idx) => (
                <button
                  key={idx}
                  className="suggestion-btn"
                  onClick={() => onSendMessage(suggestion)}
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <MessageList messages={messages} />
        )}
        
        {isLoading && (
          <div className="loading-indicator">
            <div className="typing-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>
            <span className="loading-text">Researching...</span>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <form className="input-form" onSubmit={handleSubmit}>
        <div className="input-wrapper">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask anything..."
            className="chat-input"
            disabled={isLoading}
          />
          <button 
            type="submit" 
            className="send-btn"
            disabled={!input.trim() || isLoading}
          >
            <Send size={20} />
          </button>
        </div>
      </form>
    </div>
  )
}

export default ChatPanel
