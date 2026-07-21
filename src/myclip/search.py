from pathlib import Path

import faiss
import numpy as np

from myclip.database import Database
from myclip.embeddings import embed_text


class SearchIndex:
    def __init__(self, dim: int, path: str | Path | None = None):
        self.dim = dim
        self.path = Path(path) if path else None
        self.index = faiss.IndexFlatIP(dim)  # Inner product (cosine for normalized vectors)
        self.id_map: list[int] = []

        if self.path and self.path.exists():
            self._load()

    def add(self, scene_id: int, vector: np.ndarray):
        """Add a vector to the index."""
        assert vector.shape == (self.dim,)
        # Normalize for cosine similarity
        vector = vector / np.linalg.norm(vector)
        self.index.add(vector.reshape(1, -1))
        self.id_map.append(scene_id)

    def search(self, query: np.ndarray, k: int = 10) -> list[tuple[int, float]]:
        """Search for nearest neighbors.

        Args:
            query: Query vector (512-dim).
            k: Number of results.

        Returns:
            List of (scene_id, similarity_score) tuples, sorted by score descending.
        """
        if self.index.ntotal == 0:
            return []

        query = query / np.linalg.norm(query)
        k = min(k, self.index.ntotal)
        scores, indices = self.index.search(query.reshape(1, -1), k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0 and idx < len(self.id_map):
                results.append((self.id_map[idx], float(score)))
        return results

    def save(self):
        """Save index to disk."""
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            faiss.write_index(self.index, str(self.path))
            # Save ID map separately
            map_path = self.path.with_suffix(".ids.npy")
            np.save(str(map_path), np.array(self.id_map))

    def _load(self):
        """Load index from disk."""
        self.index = faiss.read_index(str(self.path))
        map_path = self.path.with_suffix(".ids.npy")
        if map_path.exists():
            self.id_map = np.load(str(map_path)).tolist()

    @property
    def size(self) -> int:
        return self.index.ntotal


def hybrid_search(
    query: str,
    clip_index: SearchIndex,
    db: Database,
    k: int = 10,
) -> list[dict]:
    """Search combining CLIP visual similarity + FTS5 text matching.

    Scenes matching BOTH get boosted to the top.

    Args:
        query: Natural language search query.
        clip_index: FAISS CLIP vector index.
        db: Database with FTS5.
        k: Number of results.

    Returns:
        List of scene dicts with 'match_type' and 'score' added.
    """
    # CLIP visual search
    query_vec = embed_text(query)
    clip_results = clip_index.search(query_vec, k=k * 2)

    # FTS5 text search
    text_results = db.search_text(query, limit=k * 2)

    # Score normalization
    clip_scores = {}
    if clip_results:
        max_clip = max(score for _, score in clip_results)
        for scene_id, score in clip_results:
            clip_scores[scene_id] = score / max_clip if max_clip > 0 else 0

    text_scores = {}
    if text_results:
        max_text = max(score for _, score in text_results)
        for scene_id, score in text_results:
            text_scores[scene_id] = score / max_text if max_text > 0 else 0

    # Merge: scenes matching BOTH get boosted
    all_ids = set(clip_scores.keys()) | set(text_scores.keys())
    merged = []
    for scene_id in all_ids:
        c = clip_scores.get(scene_id, 0)
        t = text_scores.get(scene_id, 0)

        if c > 0 and t > 0:
            # Both match — boosted score
            score = (c * 0.5 + t * 0.5) * 1.3
            match_type = "visual+text"
        elif c > 0:
            score = c * 0.5
            match_type = "visual"
        else:
            score = t * 0.5
            match_type = "text"

        scene = db.get_scene(scene_id)
        if scene:
            scene["score"] = min(score, 1.0)
            scene["match_type"] = match_type
            merged.append(scene)

    # Sort by score descending
    merged.sort(key=lambda s: s["score"], reverse=True)
    return merged[:k]
