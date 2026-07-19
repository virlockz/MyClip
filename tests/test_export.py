import json
import subprocess
import tempfile
from pathlib import Path

from myclip.export import export_clip


def test_export_clip_creates_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        out = Path(tmpdir) / "clip.mp4"
        result = export_clip(
            "tests/fixtures/sample_video.mp4",
            start_sec=0.5,
            end_sec=2.5,
            output_path=out,
        )
        assert result.exists()
        assert result.stat().st_size > 0


def test_export_clip_duration():
    with tempfile.TemporaryDirectory() as tmpdir:
        out = Path(tmpdir) / "clip.mp4"
        export_clip("tests/fixtures/sample_video.mp4", 1.0, 3.0, out)
        probe = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json",
             "-show_format", str(out)],
            capture_output=True, text=True,
        )
        duration = float(json.loads(probe.stdout)["format"]["duration"])
        assert 1.5 < duration < 2.5  # Should be ~2 seconds
