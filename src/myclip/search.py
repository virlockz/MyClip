from pathlib import Path

import faiss
import numpy as np


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
