import { useState, useCallback, useRef } from 'react'

interface FileGroup {
  video: File | null
  subtitle: File | null
  label: string
}

interface Props {
  onUploadComplete: () => void
}

export default function DropZone({ onUploadComplete }: Props) {
  const [isDragging, setIsDragging] = useState(false)
  const [files, setFiles] = useState<FileGroup[]>([])
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState('')
  const fileInputRef = useRef<HTMLInputElement>(null)

  const videoExts = ['.mp4', '.mkv', '.avi', '.mov', '.webm']
  const subExts = ['.srt', '.ass', '.vtt', '.sub']

  const getExt = (name: string) => name.slice(name.lastIndexOf('.')).toLowerCase()
  const getStem = (name: string) => name.slice(0, name.lastIndexOf('.'))

  const handleFiles = useCallback((fileList: FileList) => {
    const newFiles = Array.from(fileList)
    setFiles(prev => {
      const updated = [...prev]

      for (const file of newFiles) {
        const ext = getExt(file.name)
        const stem = getStem(file.name)

        if (videoExts.includes(ext)) {
          // Find existing group with same stem, or create new
          const existing = updated.find(g => g.label === stem)
          if (existing) {
            existing.video = file
          } else {
            updated.push({ video: file, subtitle: null, label: stem })
          }
        } else if (subExts.includes(ext)) {
          // Find matching video group
          const existing = updated.find(g => g.label === stem)
          if (existing) {
            existing.subtitle = file
          } else {
            updated.push({ video: null, subtitle: file, label: stem })
          }
        }
      }

      return updated
    })
  }, [])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    if (e.dataTransfer.files.length > 0) {
      handleFiles(e.dataTransfer.files)
    }
  }, [handleFiles])

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index))
  }

  const handleUpload = async () => {
    const groupsToUpload = files.filter(g => g.video !== null)
    if (groupsToUpload.length === 0) return

    setUploading(true)
    setProgress(`Uploading ${groupsToUpload.length} episode(s)...`)

    try {
      const formData = new FormData()
      for (const group of groupsToUpload) {
        if (group.video) formData.append('files', group.video)
        if (group.subtitle) formData.append('files', group.subtitle)
      }

      const res = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      })

      if (!res.ok) throw new Error('Upload failed')

      const data = await res.json()
      setProgress(`Uploaded! Ingesting ${groupsToUpload.length} episode(s)...`)

      // Start ingest
      const ingestRes = await fetch('/api/ingest-uploaded', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ directory: data.directory }),
      })

      if (!ingestRes.ok) throw new Error('Ingest failed')

      setProgress('Done!')
      setFiles([])
      setTimeout(onUploadComplete, 1000)
    } catch (err) {
      setProgress('Error: Upload failed. Check the console.')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="dropzone-container">
      <div
        className={`dropzone ${isDragging ? 'dropzone-active' : ''} ${files.length > 0 ? 'dropzone-has-files' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".mp4,.mkv,.avi,.mov,.webm,.srt,.ass,.vtt,.sub,.jpg,.jpeg,.png"
          style={{ display: 'none' }}
          onChange={e => e.target.files && handleFiles(e.target.files)}
        />

        {files.length === 0 ? (
          <>
            <div className="dropzone-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="17 8 12 3 7 8"/>
                <line x1="12" y1="3" x2="12" y2="15"/>
              </svg>
            </div>
            <p className="dropzone-text">Drag video + subtitle files here</p>
            <p className="dropzone-hint">or click to browse</p>
          </>
        ) : (
          <div className="dropzone-files" onClick={e => e.stopPropagation()}>
            <div className="dropzone-files-header">
              <span>{files.length} episode(s) ready</span>
              <button className="dropzone-clear" onClick={() => setFiles([])}>Clear all</button>
            </div>

            <div className="dropzone-file-list">
              {files.map((group, i) => (
                <div key={i} className="dropzone-file-row">
                  <div className="dropzone-file-info">
                    <span className="dropzone-file-name">{group.label}</span>
                    <div className="dropzone-file-tags">
                      {group.video && <span className="tag tag-video">video</span>}
                      {group.subtitle && <span className="tag tag-sub">subs</span>}
                      {!group.video && <span className="tag tag-missing">no video</span>}
                    </div>
                  </div>
                  <button className="dropzone-remove" onClick={() => removeFile(i)}>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                    </svg>
                  </button>
                </div>
              ))}
            </div>

            {progress && <p className="dropzone-progress">{progress}</p>}

            <button
              className="dropzone-upload-btn"
              onClick={handleUpload}
              disabled={uploading || files.every(g => !g.video)}
            >
              {uploading ? 'Uploading...' : `Start Ingest (${files.filter(g => g.video).length} episodes)`}
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
