import { useState } from 'react'

interface Props {
  onClose: () => void
  onComplete: () => void
}

export default function IngestPanel({ onClose, onComplete }: Props) {
  const [path, setPath] = useState('')
  const [ingesting, setIngesting] = useState(false)
  const [output, setOutput] = useState('')

  const handleIngest = async () => {
    if (!path.trim()) return
    setIngesting(true)
    setOutput('Starting ingest...\n')

    try {
      const res = await fetch('/api/ingest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ directory: path }),
      })
      const data = await res.json()
      setOutput(data.message || 'Ingest complete!')
      if (data.success) {
        setTimeout(onComplete, 1500)
      }
    } catch {
      setOutput('Error: Could not reach the server. Make sure the backend is running.')
    } finally {
      setIngesting(false)
    }
  }

  return (
    <div className="ingest-overlay" onClick={onClose}>
      <div className="ingest-panel" onClick={e => e.stopPropagation()}>
        <div className="ingest-header">
          <h2>Add Episodes</h2>
          <button className="close-btn" onClick={onClose}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        <div className="ingest-body">
          <label className="ingest-label">Episode directory path</label>
          <input
            type="text"
            className="ingest-input"
            placeholder="C:\Users\You\Videos\The Mentalist\S01"
            value={path}
            onChange={e => setPath(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleIngest()}
            disabled={ingesting}
          />
          <p className="ingest-hint">
            Point to a folder containing .mp4 or .mkv files with matching .srt subtitle files
          </p>

          <button
            className="ingest-start"
            onClick={handleIngest}
            disabled={!path.trim() || ingesting}
          >
            {ingesting ? (
              <>
                <span className="spinner"></span>
                Processing...
              </>
            ) : (
              <>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                  <polyline points="17 8 12 3 7 8"/>
                  <line x1="12" y1="3" x2="12" y2="15"/>
                </svg>
                Start Ingest
              </>
            )}
          </button>

          {output && (
            <div className="ingest-output">
              <pre>{output}</pre>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
