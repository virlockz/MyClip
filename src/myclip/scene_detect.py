from dataclasses import dataclass
from pathlib import Path

from scenedetect import detect, ContentDetector


@dataclass
class SceneBoundary:
    start_sec: float
    end_sec: float


def detect_scenes(video_path: str | Path, threshold: float = 27.0) -> list[SceneBoundary]:
    """Detect scene boundaries in a video file.

    Args:
        video_path: Path to the video file.
        threshold: ContentDetector threshold (lower = more sensitive).

    Returns:
        Sorted list of SceneBoundary objects.
    """
    scene_list = detect(str(video_path), ContentDetector(threshold=threshold))
    return [
        SceneBoundary(
            start_sec=start.seconds,
            end_sec=end.seconds,
        )
        for start, end in scene_list
    ]
