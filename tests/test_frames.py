import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

from myclip.frames import extract_frames, dedup_thumbnail
from myclip.scene_detect import SceneBoundary


def test_extract_frames_creates_thumbnails():
    scenes = [
        SceneBoundary(start_sec=0.5, end_sec=1.5),
        SceneBoundary(start_sec=2.5, end_sec=3.5),
    ]
    with tempfile.TemporaryDirectory() as tmpdir:
        paths = extract_frames("tests/fixtures/sample_video.mp4", scenes, tmpdir)
        assert len(paths) == 2
        for p in paths:
            assert p.exists()
            assert p.suffix == ".jpg"


def test_dedup_keeps_different_frames():
    """Two different images should both be kept."""
    with tempfile.TemporaryDirectory() as tmpdir:
        img1 = Image.fromarray(np.zeros((16, 16), dtype=np.uint8))
        img2 = Image.fromarray(np.full((16, 16), 255, dtype=np.uint8))
        p1 = Path(tmpdir) / "a.jpg"
        p2 = Path(tmpdir) / "b.jpg"
        img1.save(p1)
        img2.save(p2)
        assert dedup_thumbnail(p1, None) is None  # First always kept
        assert dedup_thumbnail(p2, p1) is None    # Different = kept


def test_dedup_drops_similar_frames():
    """Nearly identical images should be dropped."""
    with tempfile.TemporaryDirectory() as tmpdir:
        img1 = Image.fromarray(np.full((16, 16), 100, dtype=np.uint8))
        img2 = Image.fromarray(np.full((16, 16), 101, dtype=np.uint8))  # diff = 1
        p1 = Path(tmpdir) / "a.jpg"
        p2 = Path(tmpdir) / "b.jpg"
        img1.save(p1)
        img2.save(p2)
        assert dedup_thumbnail(p1, None) is None   # First always kept
        result = dedup_thumbnail(p2, p1)
        assert result == p1  # Similar = dropped, return previous
