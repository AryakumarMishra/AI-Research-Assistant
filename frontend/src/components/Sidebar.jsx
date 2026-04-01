import { FileText, Globe, ChevronDown, ChevronRight } from 'lucide-react'
import { useState } from 'react'
import './Sidebar.css'

function Sidebar({ sources, findings }) {
  const [showFindings, setShowFindings] = useState(true)
  const [showSources, setShowSources] = useState(true)

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h3 className="sidebar-title">Research Details</h3>
      </div>

      {/* Findings Section */}
      <div className="sidebar-section">
        <button 
          className="section-toggle"
          onClick={() => setShowFindings(!showFindings)}
        >
          <div className="section-title">
            <FileText size={18} />
            <span>Findings ({findings.length})</span>
          </div>
          {showFindings ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
        </button>
        
        {showFindings && (
          <div className="section-content">
            {findings.length === 0 ? (
              <p className="empty-state">No findings yet. Start a research query.</p>
            ) : (
              <ul className="findings-list">
                {findings.map((finding, idx) => (
                  <li key={idx} className="finding-item">
                    <span className="finding-number">{idx + 1}</span>
                    <p className="finding-text">{finding}</p>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
      </div>

      {/* Sources Section */}
      <div className="sidebar-section">
        <button 
          className="section-toggle"
          onClick={() => setShowSources(!showSources)}
        >
          <div className="section-title">
            <Globe size={18} />
            <span>Sources ({sources.length})</span>
          </div>
          {showSources ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
        </button>
        
        {showSources && (
          <div className="section-content">
            {sources.length === 0 ? (
              <p className="empty-state">No sources collected yet.</p>
            ) : (
              <ul className="sources-list">
                {sources.map((source, idx) => (
                  <li key={idx} className="source-item">
                    {source.title ? (
                      <a 
                        href={source.url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="source-link"
                      >
                        <span className="source-title">{source.title}</span>
                        {source.authors && (
                          <span className="source-meta">
                            {source.authors.slice(0, 2).join(', ')}
                            {source.authors.length > 2 && ' et al.'}
                          </span>
                        )}
                      </a>
                    ) : (
                      <span className="source-text">{JSON.stringify(source)}</span>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
      </div>
    </aside>
  )
}

export default Sidebar
