interface Props {
  scene: any
}

function MatchBadge({ type }: { type: string }) {
  if (!type) return null

  const config: Record<string, { label: string; className: string }> = {
    'visual+text': { label: 'V+T', className: 'match-both' },
    'visual': { label: 'V', className: 'match-visual' },
    'text': { label: 'T', className: 'match-text' },
  }

  const { label, className } = config[type] || { label: type, className: '' }
  return <span className={`scene-match ${className}`}>{label}</span>
}

export default function SceneCard({ scene }: Props) {
  const thumbFilename = scene.thumbnail_path?.split(/[/\\]/).pop() || ''

  return (
    <div className="scene-card">
      <img
        src={`/api/thumbnails/${thumbFilename}`}
        alt={`Scene ${scene.scene_number}`}
        className="scene-thumb"
        loading="lazy"
      />
      <div className="scene-info">
        <div className="scene-meta">
          <span className="scene-episode">{scene.episode}</span>
          <span className="scene-time">
            {scene.start_time?.toFixed(1)}s — {scene.end_time?.toFixed(1)}s
          </span>
        </div>
        <p className="scene-dialogue">
          {scene.subtitle_text || 'No dialogue'}
        </p>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginTop: '6px' }}>
          <MatchBadge type={scene.match_type} />
          {scene.score !== undefined && (
            <span style={{ fontSize: '10px', color: 'var(--text-muted)' }}>
              {(scene.score * 100).toFixed(0)}%
            </span>
          )}
        </div>
      </div>
    </div>
  )
}
