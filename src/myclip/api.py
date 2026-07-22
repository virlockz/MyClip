import shutil
import tempfile
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel

from myclip.database import Database
from myclip.search import SearchIndex, hybrid_search
from myclip.export import export_clip
from myclip.ingest import ingest_directory
from myclip.config import CLIPS_DIR, THUMBNAILS_DIR, DB_PATH, FAISS_PATH, EMBEDDING_DIM, DATA_DIR


class ExportRequest(BaseModel):
    episode: str
    scenes: list[int]


def create_app(db: Database | None = None, index: SearchIndex | None = None) -> FastAPI:
    if db is None:
        db = Database(DB_PATH)
    if index is None:
        index = SearchIndex(dim=EMBEDDING_DIM, path=FAISS_PATH)
    app = FastAPI(title="MyClip", version="0.1.0")

    @app.get("/api/scenes")
    def list_scenes(episode: str | None = None, season: int | None = None):
        scenes = db.get_scenes(episode=episode, season=season)
        return {"scenes": scenes, "count": len(scenes)}

    @app.get("/api/scenes/{scene_id}")
    def get_scene(scene_id: int):
        scene = db.get_scene(scene_id)
        if not scene:
            raise HTTPException(404, "Scene not found")
        return scene

    @app.get("/api/search")
    def search(q: str, limit: int = 10):
        results = hybrid_search(q, index, db, k=limit)
        return {"query": q, "results": results}

    @app.post("/api/export")
    def export_scenes(req: ExportRequest):
        scenes = db.get_scenes(episode=req.episode)
        exported = []
        for s in scenes:
            if s["scene_number"] in req.scenes:
                out = CLIPS_DIR / f"{req.episode}_scene{s['scene_number']}.mp4"
                export_clip(s["video_path"], s["start_time"], s["end_time"], out)
                exported.append(str(out))
        return {"exported": exported}

    @app.get("/api/thumbnails/{filename}")
    def get_thumbnail(filename: str):
        # Search for thumbnail in all episode directories
        for episode_dir in THUMBNAILS_DIR.iterdir():
            if episode_dir.is_dir():
                path = episode_dir / filename
                if path.exists():
                    return FileResponse(path, media_type="image/jpeg")
        raise HTTPException(404, "Thumbnail not found")

    @app.post("/api/upload")
    async def upload_files(files: list[UploadFile] = File(...)):
        upload_dir = DATA_DIR / "uploads" / tempfile.mkdtemp()
        upload_dir.mkdir(parents=True, exist_ok=True)

        for upload in files:
            filename = upload.filename or "unknown"
            dest = upload_dir / filename
            with open(dest, "wb") as f:
                content = await upload.read()
                f.write(content)

        return {"directory": str(upload_dir), "files": len(files)}

    @app.post("/api/ingest-uploaded")
    def ingest_uploaded(req: dict):
        directory = req.get("directory")
        if not directory:
            raise HTTPException(400, "directory is required")

        dir_path = Path(directory)
        if not dir_path.exists():
            raise HTTPException(404, "Upload directory not found")

        count = ingest_directory(dir_path, db, index)
        return {"success": True, "scenes": count}

    return app


# Module-level app for uvicorn
app = create_app()
