from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from myclip.database import Database
from myclip.search import SearchIndex
from myclip.embeddings import embed_text
from myclip.export import export_clip
from myclip.config import CLIPS_DIR, THUMBNAILS_DIR


class ExportRequest(BaseModel):
    episode: str
    scenes: list[int]


def create_app(db: Database, index: SearchIndex) -> FastAPI:
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
        query_vec = embed_text(q)
        results = index.search(query_vec, k=limit)
        scenes = []
        for scene_id, score in results:
            scene = db.get_scene(scene_id)
            if scene:
                scene["score"] = score
                scenes.append(scene)
        return {"query": q, "results": scenes}

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

    return app
