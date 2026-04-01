import { BookOpen, Trash2, PanelRight } from 'lucide-react'
import './Header.css'

function Header({ onToggleSidebar, onClearChat, messageCount }) {
  return (
    <header className="header">
      <div className="header-left">
        <div className="logo">
          <BookOpen className="logo-icon" />
          <span className="logo-text">AI Research Assistant</span>
        </div>
      </div>
      
      <div className="header-right">
        {messageCount > 0 && (
          <span className="message-count">{messageCount} messages</span>
        )}
        
        <button 
          className="header-btn"
          onClick={onClearChat}
          title="Clear chat"
        >
          <Trash2 size={18} />
        </button>
        
        <button 
          className="header-btn"
          onClick={onToggleSidebar}
          title="Toggle sidebar"
        >
          <PanelRight size={18} />
        </button>
      </div>
    </header>
  )
}

export default Header
