from dataclasses import dataclass
from pathlib import Path

import pysrt


@dataclass
class SubtitleEntry:
    start_sec: float
    end_sec: float
    text: str


def parse_srt(path: str | Path) -> list[SubtitleEntry]:
    """Parse an SRT subtitle file."""
    path = Path(path)
    if not path.exists():
        return []

    subs = pysrt.open(str(path))
    entries = []
    for sub in subs:
        start = sub.start.ordinal / 1000.0
        end = sub.end.ordinal / 1000.0
        text = sub.text.replace("\n", " ").strip()
        if text:
            entries.append(SubtitleEntry(start_sec=start, end_sec=end, text=text))
    return entries


def align_to_scenes(
    subtitles: list[SubtitleEntry],
    scenes: list,
) -> list[str]:
    """Match subtitle entries to scene time ranges.

    Args:
        subtitles: Parsed subtitle entries.
        scenes: List of SceneBoundary objects.

    Returns:
        List of concatenated dialogue strings, one per scene.
    """
    dialogues = []
    for scene in scenes:
        parts = []
        for sub in subtitles:
            # Subtitle overlaps if it starts before scene ends AND ends after scene starts
            if sub.start_sec < scene.end_sec and sub.end_sec > scene.start_sec:
                parts.append(sub.text)
        dialogues.append(" ".join(parts))
    return dialogues
