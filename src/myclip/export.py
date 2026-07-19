import subprocess
from pathlib import Path


def export_clip(
    video_path: str | Path,
    start_sec: float,
    end_sec: float,
    output_path: str | Path,
) -> Path:
    """Cut a clip from a video file.

    Args:
        video_path: Source video file.
        start_sec: Start time in seconds.
        end_sec: End time in seconds.
        output_path: Where to save the clip.

    Returns:
        Path to the exported clip.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    duration = end_sec - start_sec

    subprocess.run(
        [
            "ffmpeg", "-y",
            "-ss", str(start_sec),
            "-i", str(video_path),
            "-t", str(duration),
            "-c:v", "libx264",
            "-c:a", "aac",
            "-avoid_negative_ts", "make_zero",
            str(output_path),
        ],
        capture_output=True,
        check=True,
    )

    return output_path
