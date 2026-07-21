interface Props {
  episodes: string[]
  selectedEpisode: string | null
  onSelect: (ep: string | null) => void
  onIngest: () => void
}

export default function Sidebar({ episodes, selectedEpisode, onSelect, onIngest }: Props) {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
            <rect x="2" y="2" width="20" height="20" rx="2"/>
            <path d="M7 2v20M17 2v20M2 12h20M2 7h5M2 17h5M17 7h5M17 17h5"/>
          </svg>
        </div>
        <h2 className="sidebar-title">Episodes</h2>
      </div>

      <div className="sidebar-content">
        {episodes.length === 0 ? (
          <div className="sidebar-empty">
            <p>No episodes yet</p>
            <button className="ingest-btn" onClick={onIngest}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 5v14M5 12h14"/>
              </svg>
              Ingest episodes
            </button>
          </div>
        ) : (
          <ul className="episode-list">
            <li
              className={`episode-item ${selectedEpisode === null ? 'episode-active' : ''}`}
              onClick={() => onSelect(null)}
            >
              <span className="episode-icon">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/>
                  <rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/>
                </svg>
              </span>
              All Episodes
            </li>
            {episodes.map(ep => (
              <li
                key={ep}
                className={`episode-item ${selectedEpisode === ep ? 'episode-active' : ''}`}
                onClick={() => onSelect(ep)}
              >
                <span className="episode-icon">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polygon points="5 3 19 12 5 21 5 3"/>
                  </svg>
                </span>
                {ep}
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="sidebar-footer">
        <button className="ingest-btn-full" onClick={onIngest}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="17 8 12 3 7 8"/>
            <line x1="12" y1="3" x2="12" y2="15"/>
          </svg>
          Add Episodes
        </button>
      </div>
    </aside>
  )
}
