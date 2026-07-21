import SceneCard from './SceneCard'

interface Props {
  scenes: any[]
}

export default function SceneGrid({ scenes }: Props) {
  if (scenes.length === 0) {
    return null
  }

  return (
    <div className="scene-grid">
      {scenes.map((scene) => (
        <SceneCard key={scene.id} scene={scene} />
      ))}
    </div>
  )
}
