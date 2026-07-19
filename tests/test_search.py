import tempfile

import numpy as np

from myclip.search import SearchIndex


def test_add_and_search():
    with tempfile.TemporaryDirectory() as tmpdir:
        idx = SearchIndex(dim=512, path=f"{tmpdir}/test.faiss")
        idx.add(1, np.random.randn(512).astype(np.float32))
        idx.add(2, np.random.randn(512).astype(np.float32))
        query = np.random.randn(512).astype(np.float32)
        results = idx.search(query, k=2)
        assert len(results) == 2
        assert all(isinstance(r[0], int) for r in results)
        assert all(isinstance(r[1], float) for r in results)


def test_search_returns_sorted():
    with tempfile.TemporaryDirectory() as tmpdir:
        idx = SearchIndex(dim=4, path=f"{tmpdir}/test.faiss")
        # Add vectors where we know the similarity order
        vec_a = np.array([1, 0, 0, 0], dtype=np.float32)
        vec_b = np.array([0, 1, 0, 0], dtype=np.float32)
        vec_q = np.array([0.9, 0.1, 0, 0], dtype=np.float32)  # Closer to A
        idx.add(10, vec_a)
        idx.add(20, vec_b)
        results = idx.search(vec_q, k=2)
        assert results[0][0] == 10  # A is closest
