import { useState } from 'react'
import SearchBar from './components/SearchBar'
import SceneGrid from './components/SceneGrid'

function App() {
  const [results, setResults] = useState<any[]>([])
  const [loading, setLoading] = useState(false)

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <h1 className="text-3xl font-bold mb-8">MyClip</h1>
      <SearchBar onResults={setResults} loading={loading} setLoading={setLoading} />
      <SceneGrid scenes={results} />
    </div>
  )
}

export default App
