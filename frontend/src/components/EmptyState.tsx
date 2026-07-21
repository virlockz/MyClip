interface Props {
  onIngest: () => void
}

export default function EmptyState({ onIngest }: Props) {
  return (
    <div className="empty-state">
      <div className="empty-icon">
        <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="0.8">
          {/* Film strip */}
          <rect x="2" y="4" width="20" height="16" rx="2"/>
          <line x1="6" y1="4" x2="6" y2="20"/>
          <line x1="18" y1="4" x2="18" y2="20"/>
          <rect x="4" y="6" width="1" height="2" fill="currentColor" opacity="0.3"/>
          <rect x="4" y="10" width="1" height="2" fill="currentColor" opacity="0.3"/>
          <rect x="4" y="14" width="1" height="2" fill="currentColor" opacity="0.3"/>
          <rect x="19" y="6" width="1" height="2" fill="currentColor" opacity="0.3"/>
          <rect x="19" y="10" width="1" height="2" fill="currentColor" opacity="0.3"/>
          <rect x="19" y="14" width="1" height="2" fill="currentColor" opacity="0.3"/>
          {/* Magnifying glass */}
          <circle cx="11" cy="11" r="3" strokeWidth="1.5"/>
          <line x1="13.5" y1="13.5" x2="16" y2="16" strokeWidth="1.5"/>
        </svg>
      </div>

      <h2 className="empty-title">Start by adding episodes</h2>
      <p className="empty-desc">
        MyClip splits your videos into individual scenes and lets you
        search them by description. Add your first episode to get started.
      </p>

      <button className="empty-cta" onClick={onIngest}>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
          <polyline points="17 8 12 3 7 8"/>
          <line x1="12" y1="3" x2="12" y2="15"/>
        </svg>
        Add your first episode
      </button>

      <div className="empty-features">
        <div className="feature">
          <div className="feature-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <rect x="2" y="2" width="20" height="20" rx="2"/>
              <path d="M7 2v20M17 2v20M2 12h20"/>
            </svg>
          </div>
          <div>
            <h3>Scene Detection</h3>
            <p>Automatically finds every scene boundary in your episodes</p>
          </div>
        </div>
        <div className="feature">
          <div className="feature-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
            </svg>
          </div>
          <div>
            <h3>Visual + Text Search</h3>
            <p>Find scenes by describing what you want to see or hear</p>
          </div>
        </div>
        <div className="feature">
          <div className="feature-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="7 10 12 15 17 10"/>
              <line x1="12" y1="15" x2="12" y2="3"/>
            </svg>
          </div>
          <div>
            <h3>Export Clips</h3>
            <p>Download individual scenes as MP4 files</p>
          </div>
        </div>
      </div>

      <div className="empty-cli">
        <p className="cli-label">Or use the command line:</p>
        <code className="cli-command">myclip ingest /path/to/your/episodes/</code>
      </div>
    </div>
  )
}
