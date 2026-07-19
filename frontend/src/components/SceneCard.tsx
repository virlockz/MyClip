interface Props {
  scene: any
}

export default function SceneCard({ scene }: Props) {
  return (
    <div className="bg-gray-800 rounded-lg overflow-hidden border border-gray-700 hover:border-blue-500 transition">
      <img
        src={`/api/thumbnails/${scene.thumbnail_path?.split('/').pop()}`}
        alt={`Scene ${scene.scene_number}`}
        className="w-full h-40 object-cover"
      />
      <div className="p-3">
        <div className="text-sm text-blue-400 mb-1">
          {scene.episode} — Scene {scene.scene_number}
        </div>
        <div className="text-xs text-gray-400 mb-1">
          {scene.start_time?.toFixed(1)}s — {scene.end_time?.toFixed(1)}s
        </div>
        <p className="text-sm text-gray-300 line-clamp-2">
          {scene.subtitle_text || 'No dialogue'}
        </p>
        {scene.score !== undefined && (
          <div className="text-xs text-green-400 mt-1">
            Match: {(scene.score * 100).toFixed(0)}%
          </div>
        )}
      </div>
    </div>
  )
}
