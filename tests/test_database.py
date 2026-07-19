import tempfile
from pathlib import Path

from myclip.database import Database


def test_init_db_creates_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        db = Database(Path(tmpdir) / "test.db")
        assert Path(tmpdir, "test.db").exists()
        db.close()


def test_insert_and_get_scene():
    with tempfile.TemporaryDirectory() as tmpdir:
        db = Database(Path(tmpdir) / "test.db")
        scene_id = db.insert_scene(
            episode="S01E03",
            season=1,
            episode_num=3,
            scene_number=47,
            start_time=12.5,
            end_time=18.3,
            subtitle_text="Hello there.",
            thumbnail_path="/thumbs/s01e03_47.jpg",
            video_path="/videos/s01e03.mp4",
        )
        scene = db.get_scene(scene_id)
        assert scene is not None
        assert scene["episode"] == "S01E03"
        assert scene["scene_number"] == 47
        db.close()


def test_get_scenes_by_episode():
    with tempfile.TemporaryDirectory() as tmpdir:
        db = Database(Path(tmpdir) / "test.db")
        db.insert_scene(episode="S01E03", season=1, episode_num=3,
                        scene_number=1, start_time=0, end_time=5,
                        subtitle_text="A", thumbnail_path="", video_path="")
        db.insert_scene(episode="S01E03", season=1, episode_num=3,
                        scene_number=2, start_time=5, end_time=10,
                        subtitle_text="B", thumbnail_path="", video_path="")
        db.insert_scene(episode="S02E01", season=2, episode_num=1,
                        scene_number=1, start_time=0, end_time=5,
                        subtitle_text="C", thumbnail_path="", video_path="")
        scenes = db.get_scenes(episode="S01E03")
        assert len(scenes) == 2
        db.close()
