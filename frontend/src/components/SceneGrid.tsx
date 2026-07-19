import SceneCard from './SceneCard'

interface Props {
  scenes: any[]
}

export default function SceneGrid({ scenes }: Props) {
  if (scenes.length === 0) {
    return <p className="text-gray-500">No scenes found. Try searching for something.</p>
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
      {scenes.map((scene) => (
        <SceneCard key={scene.id} scene={scene} />
      ))}
    </div>
  )
}
