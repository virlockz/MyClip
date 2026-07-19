from myclip.subtitles import parse_srt, align_to_scenes
from myclip.scene_detect import SceneBoundary


def test_parse_srt_returns_entries():
    entries = parse_srt("tests/fixtures/sample.srt")
    assert len(entries) == 3
    assert entries[0].text == "Hello, this is scene one."


def test_parse_srt_handles_missing_file():
    entries = parse_srt("nonexistent.srt")
    assert entries == []


def test_align_to_scenes_matches_dialogue():
    entries = parse_srt("tests/fixtures/sample.srt")
    scenes = [
        SceneBoundary(start_sec=0.0, end_sec=3.0),
        SceneBoundary(start_sec=3.0, end_sec=6.0),
    ]
    dialogues = align_to_scenes(entries, scenes)
    assert len(dialogues) == 2
    assert "Hello" in dialogues[0]
    assert "scene two" in dialogues[1]


def test_align_empty_subtitles():
    scenes = [SceneBoundary(start_sec=0.0, end_sec=5.0)]
    dialogues = align_to_scenes([], scenes)
    assert dialogues == [""]
