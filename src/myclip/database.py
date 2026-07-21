import json
import sqlite3
from pathlib import Path


class Database:
    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS scenes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                episode TEXT NOT NULL,
                season INTEGER NOT NULL,
                episode_num INTEGER NOT NULL,
                scene_number INTEGER NOT NULL,
                start_time REAL NOT NULL,
                end_time REAL NOT NULL,
                duration REAL GENERATED ALWAYS AS (end_time - start_time) STORED,
                subtitle_text TEXT DEFAULT '',
                thumbnail_path TEXT DEFAULT '',
                video_path TEXT DEFAULT '',
                yolo_objects TEXT DEFAULT '[]',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_episode ON scenes(episode);
            CREATE INDEX IF NOT EXISTS idx_season ON scenes(season);
        """)
        # FTS5 virtual table for full-text search on subtitles
        self.conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS scenes_fts USING fts5(
                subtitle_text,
                content='scenes',
                content_rowid='id'
            );
        """)
        # Triggers to keep FTS index in sync
        self.conn.executescript("""
            CREATE TRIGGER IF NOT EXISTS scenes_ai AFTER INSERT ON scenes BEGIN
                INSERT INTO scenes_fts(rowid, subtitle_text) VALUES (new.id, new.subtitle_text);
            END;
            CREATE TRIGGER IF NOT EXISTS scenes_ad AFTER DELETE ON scenes BEGIN
                INSERT INTO scenes_fts(scenes_fts, rowid, subtitle_text) VALUES('delete', old.id, old.subtitle_text);
            END;
            CREATE TRIGGER IF NOT EXISTS scenes_au AFTER UPDATE ON scenes BEGIN
                INSERT INTO scenes_fts(scenes_fts, rowid, subtitle_text) VALUES('delete', old.id, old.subtitle_text);
                INSERT INTO scenes_fts(rowid, subtitle_text) VALUES (new.id, new.subtitle_text);
            END;
        """)
        self.conn.commit()

    def insert_scene(
        self,
        episode: str,
        season: int,
        episode_num: int,
        scene_number: int,
        start_time: float,
        end_time: float,
        subtitle_text: str = "",
        thumbnail_path: str = "",
        video_path: str = "",
        yolo_objects: list[str] | None = None,
    ) -> int:
        cursor = self.conn.execute(
            """INSERT INTO scenes
               (episode, season, episode_num, scene_number, start_time, end_time,
                subtitle_text, thumbnail_path, video_path, yolo_objects)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                episode, season, episode_num, scene_number,
                start_time, end_time, subtitle_text,
                thumbnail_path, video_path,
                json.dumps(yolo_objects or []),
            ),
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_scene(self, scene_id: int) -> dict | None:
        row = self.conn.execute(
            "SELECT * FROM scenes WHERE id = ?", (scene_id,)
        ).fetchone()
        return dict(row) if row else None

    def get_scenes(self, episode: str | None = None, season: int | None = None) -> list[dict]:
        query = "SELECT * FROM scenes WHERE 1=1"
        params = []
        if episode:
            query += " AND episode = ?"
            params.append(episode)
        if season:
            query += " AND season = ?"
            params.append(season)
        query += " ORDER BY season, episode_num, scene_number"
        rows = self.conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]

    def get_all_scenes(self) -> list[dict]:
        return self.get_scenes()

    def search_text(self, query: str, limit: int = 10) -> list[tuple[int, float]]:
        """Full-text search on subtitle text using FTS5.

        Args:
            query: Search query (supports phrases in quotes).
            limit: Max results.

        Returns:
            List of (scene_id, bm25_score) tuples, sorted by relevance.
        """
        try:
            rows = self.conn.execute(
                """SELECT rowid, bm25(scenes_fts) as score
                   FROM scenes_fts
                   WHERE scenes_fts MATCH ?
                   ORDER BY score
                   LIMIT ?""",
                (query, limit),
            ).fetchall()
            return [(row["rowid"], -row["score"]) for row in rows]
        except sqlite3.OperationalError:
            # FTS5 query syntax error — fall back to simple LIKE
            rows = self.conn.execute(
                """SELECT id, 1.0 as score
                   FROM scenes
                   WHERE subtitle_text LIKE ?
                   LIMIT ?""",
                (f"%{query}%", limit),
            ).fetchall()
            return [(row["id"], row["score"]) for row in rows]

    def close(self):
        self.conn.close()
