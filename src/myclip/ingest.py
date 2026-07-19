import re
from pathlib import Path

from myclip.scene_detect import detect_scenes
from myclip.subtitles import parse_srt, align_to_scenes
from myclip.frames import extract_frames
from myclip.embeddings import embed_image
from myclip.objects import detect_objects
from myclip.database import Database
from myclip.search import SearchIndex
from myclip.config import DEFAULT_THRESHOLD, THUMBNAILS_DIR


def parse_episode_filename(filename: str) -> tuple[int, int] | None:
    """Extract season and episode from filename patterns like S01E03, 1x03."""
    patterns = [
        r"[Ss](\d+)[Ee](\d+)",   # S01E03, s01e03
        r"(\d+)[xX](\d+)",       # 1x03, 1X03
    ]
    for pattern in patterns:
        match = re.search(pattern, filename)
        if match:
            return int(match.group(1)), int(match.group(2))
    return None


def find_subtitle(video_path: Path) -> Path | None:
    """Find matching subtitle file for a video."""
    stem = video_path.stem
    for ext in [".srt", ".ass", ".vtt"]:
        sub_path = video_path.parent / f"{stem}{ext}"
        if sub_path.exists():
            return sub_path
    return None


def ingest_directory(
    dir_path: str | Path,
    db: Database,
    index: SearchIndex,
    threshold: float = DEFAULT_THRESHOLD,
) -> int:
    """Ingest all episodes from a directory.

    Args:
        dir_path: Directory containing video files.
        db: Database instance.
        index: FAISS search index.
        threshold: Scene detection threshold.

    Returns:
        Total number of scenes indexed.
    """
    dir_path = Path(dir_path)
    video_exts = {".mp4", ".mkv", ".avi", ".mov"}
    video_files = sorted(
        f for f in dir_path.iterdir()
        if f.suffix.lower() in video_exts
    )

    total_scenes = 0

    for video_path in video_files:
        episode_info = parse_episode_filename(video_path.name)
        if not episode_info:
            print(f"Skipping {video_path.name} — can't parse episode number")
            continue

        season, episode_num = episode_info
        episode_label = f"S{season:02d}E{episode_num:02d}"

        # Detect scenes
        scenes = detect_scenes(video_path, threshold=threshold)

        # Parse subtitles
        sub_path = find_subtitle(video_path)
        subtitles = parse_srt(sub_path) if sub_path else []
        dialogues = align_to_scenes(subtitles, scenes) if subtitles else [""] * len(scenes)

        # Extract frames + embed
        thumb_dir = THUMBNAILS_DIR / episode_label
        thumbnails = extract_frames(video_path, scenes, thumb_dir)

        for i, (scene, dialogue, thumb_path) in enumerate(zip(scenes, dialogues, thumbnails)):
            # Detect objects (optional, skip on error)
            yolo_objects = []
            try:
                yolo_objects = detect_objects(thumb_path)
            except Exception:
                pass

            # Generate CLIP embedding
            embedding = embed_image(thumb_path)

            # Insert into database
            scene_id = db.insert_scene(
                episode=episode_label,
                season=season,
                episode_num=episode_num,
                scene_number=i + 1,
                start_time=scene.start_sec,
                end_time=scene.end_sec,
                subtitle_text=dialogue,
                thumbnail_path=str(thumb_path),
                video_path=str(video_path),
                yolo_objects=yolo_objects,
            )

            # Add to FAISS index
            index.add(scene_id, embedding)

            total_scenes += 1

        print(f"{episode_label}: {len(scenes)} scenes indexed")

    # Save index
    index.save()

    return total_scenes
