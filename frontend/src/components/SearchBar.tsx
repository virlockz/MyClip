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
    <div className="flex gap-4 mb-8">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
        placeholder="Describe a scene... (e.g., 'Jane interrogating someone')"
        className="flex-1 px-4 py-3 rounded-lg bg-gray-800 border border-gray-700 text-white"
      />
      <button
        onClick={handleSearch}
        disabled={loading}
        className="px-6 py-3 bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50"
      >
        {loading ? 'Searching...' : 'Search'}
      </button>
    </div>
  )
}
