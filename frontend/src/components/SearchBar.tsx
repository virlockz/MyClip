import { useState } from 'react'
import { searchScenes } from '../hooks/useApi'

interface Props {
  onResults: (scenes: any[]) => void
  loading: boolean
  setLoading: (v: boolean) => void
}

export default function SearchBar({ onResults, loading, setLoading }: Props) {
  const [query, setQuery] = useState('')

  const handleSearch = async () => {
    if (!query.trim()) return
    setLoading(true)
    const results = await searchScenes(query)
    onResults(results)
    setLoading(false)
  }

  return (
    <div className="search-container">
      <div className="search-wrapper" style={{ position: 'relative' }}>
        <svg className="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
        </svg>
        <input
          type="text"
          className="search-input"
          placeholder="Search scenes... (e.g., &quot;Red John&quot;, &quot;Jane interrogating&quot;)"
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleSearch()}
        />
        <button
          className="search-btn"
          onClick={handleSearch}
          disabled={loading || !query.trim()}
        >
          {loading ? 'Searching...' : 'Search'}
        </button>
      </div>
    </div>
  )
}
