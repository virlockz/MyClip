import { useState, useEffect } from 'react'
import SearchBar from './components/SearchBar'
import SceneGrid from './components/SceneGrid'
import Sidebar from './components/Sidebar'
import EmptyState from './components/EmptyState'
import IngestPanel from './components/IngestPanel'

function App() {
  const [results, setResults] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [episodes, setEpisodes] = useState<string[]>([])
  const [selectedEpisode, setSelectedEpisode] = useState<string | null>(null)
  const [episodeScenes, setEpisodeScenes] = useState<any[]>([])
  const [hasData, setHasData] = useState(false)
  const [showIngest, setShowIngest] = useState(false)
  const [activeTab, setActiveTab] = useState<'search' | 'browse'>('search')

  useEffect(() => {
    fetch('/api/scenes')
      .then(r => r.json())
      .then(data => {
        if (data.scenes && data.scenes.length > 0) {
          setHasData(true)
          const eps = [...new Set(data.scenes.map((s: any) => s.episode))] as string[]
          setEpisodes(eps.sort())
        }
      })
      .catch(() => {})
  }, [])

  useEffect(() => {
    if (selectedEpisode) {
      fetch(`/api/scenes?episode=${selectedEpisode}`)
        .then(r => r.json())
        .then(data => setEpisodeScenes(data.scenes || []))
        .catch(() => {})
    }
  }, [selectedEpisode])

  const displayScenes = activeTab === 'search' ? results : episodeScenes

  return (
    <div className="app-layout">
      <Sidebar
        episodes={episodes}
        selectedEpisode={selectedEpisode}
        onSelect={setSelectedEpisode}
        onIngest={() => setShowIngest(true)}
      />
      <main className="main-content">
        <header className="main-header">
          <div className="header-left">
            <h1 className="app-title">
              <span className="title-accent">My</span>Clip
            </h1>
            <p className="app-subtitle">Scene-based video clipper</p>
          </div>
          {hasData && (
            <div className="tab-bar">
              <button
                className={`tab ${activeTab === 'search' ? 'tab-active' : ''}`}
                onClick={() => setActiveTab('search')}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
                </svg>
                Search
              </button>
              <button
                className={`tab ${activeTab === 'browse' ? 'tab-active' : ''}`}
                onClick={() => setActiveTab('browse')}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/>
                  <rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/>
                </svg>
                Browse
              </button>
            </div>
          )}
        </header>

        {activeTab === 'search' && (
          <SearchBar onResults={setResults} loading={loading} setLoading={setLoading} />
        )}

        {!hasData && !showIngest && (
          <EmptyState onIngest={() => setShowIngest(true)} />
        )}

        {showIngest && (
          <IngestPanel onClose={() => setShowIngest(false)} onComplete={() => {
            setShowIngest(false)
            window.location.reload()
          }} />
        )}

        {hasData && displayScenes.length > 0 && (
          <SceneGrid scenes={displayScenes} />
        )}

        {hasData && displayScenes.length === 0 && activeTab === 'search' && !loading && (
          <div className="no-results">
            <p>Type a description to search scenes</p>
            <div className="search-examples">
              <span className="example" onClick={() => {
                const input = document.querySelector('.search-input') as HTMLInputElement
                if (input) { input.value = 'Red John'; input.dispatchEvent(new Event('input', { bubbles: true })) }
              }}>Red John</span>
              <span className="example" onClick={() => {
                const input = document.querySelector('.search-input') as HTMLInputElement
                if (input) { input.value = 'Jane interrogating'; input.dispatchEvent(new Event('input', { bubbles: true })) }
              }}>Jane interrogating</span>
              <span className="example" onClick={() => {
                const input = document.querySelector('.search-input') as HTMLInputElement
                if (input) { input.value = 'CBI bullpen'; input.dispatchEvent(new Event('input', { bubbles: true })) }
              }}>CBI bullpen</span>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default App
