from pathlib import Path
import subprocess

import numpy as np
from PIL import Image

from myclip.config import DEDUP_THRESHOLD, DEDUP_THUMB_SIZE


def extract_frames(
    video_path: str | Path,
    scenes: list,
    out_dir: str | Path,
    dedup: bool = True,
) -> list[Path]:
    """Extract one representative frame per scene.

    Args:
        video_path: Path to the source video.
        scenes: List of SceneBoundary objects.
        out_dir: Directory to save thumbnails.
        dedup: Whether to apply deduplication.

    Returns:
        List of paths to kept thumbnail JPEGs.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    thumbnails = []
    last_kept = None

    for i, scene in enumerate(scenes):
        mid_time = (scene.start_sec + scene.end_sec) / 2
        thumb_path = out_dir / f"scene_{i:04d}.jpg"

        # Extract frame at midpoint
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-ss", str(mid_time),
                "-i", str(video_path),
                "-frames:v", "1",
                "-q:v", "2",
                str(thumb_path),
            ],
            capture_output=True,
            check=True,
        )

        if dedup:
            result = dedup_thumbnail(thumb_path, last_kept)
            if result is None:
                # Frame was kept (different enough)
                last_kept = thumb_path
                thumbnails.append(thumb_path)
            else:
                # Frame was dropped (too similar)
                thumb_path.unlink(missing_ok=True)
        else:
            thumbnails.append(thumb_path)
            last_kept = thumb_path

    return thumbnails


def dedup_thumbnail(
    current: Path,
    previous: Path | None,
) -> Path | None:
    """Check if current frame is a near-duplicate of previous.

    Uses 16x16 grayscale thumbnail + mean absolute difference.

    Args:
        current: Path to current frame JPEG.
        previous: Path to last kept frame JPEG (None for first frame).

    Returns:
        previous path if current is a duplicate (should be dropped).
        None if current is different enough (should be kept).
    """
    if previous is None:
        return None  # First frame always kept

    curr_img = _load_grayscale_thumb(current)
    prev_img = _load_grayscale_thumb(previous)

    diff = float(np.mean(np.abs(curr_img.astype(float) - prev_img.astype(float))))

    if diff <= DEDUP_THRESHOLD:
        return previous  # Too similar, drop current
    return None  # Different enough, keep current


def _load_grayscale_thumb(path: Path) -> np.ndarray:
    """Load image as 16x16 grayscale numpy array."""
    img = Image.open(path).convert("L")
    img = img.resize((DEDUP_THUMB_SIZE, DEDUP_THUMB_SIZE), Image.Resampling.LANCZOS)
    return np.array(img)
