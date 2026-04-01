import { User, Bot, AlertCircle } from 'lucide-react'
import './MessageList.css'

function MessageList({ messages }) {
  const formatTime = (date) => {
    return new Intl.DateTimeFormat('en-US', {
      hour: 'numeric',
      minute: 'numeric',
      hour12: true
    }).format(date)
  }

  return (
    <div className="message-list">
      {messages.map((message, index) => (
        <div 
          key={index} 
          className={`message ${message.role} ${message.isError ? 'error' : ''}`}
        >
          <div className="message-avatar">
            {message.role === 'user' ? (
              <User size={18} />
            ) : message.isError ? (
              <AlertCircle size={18} />
            ) : (
              <Bot size={18} />
            )}
          </div>
          
          <div className="message-content">
            <div className="message-header">
              <span className="message-author">
                {message.role === 'user' ? 'You' : 'Research Assistant'}
              </span>
              <span className="message-time">
                {formatTime(message.timestamp)}
              </span>
            </div>
            
            <div className="message-body">
              {message.content}
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

export default MessageList
