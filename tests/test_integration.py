import tempfile
from pathlib import Path

from myclip.database import Database
from myclip.search import SearchIndex
from myclip.ingest import ingest_directory
from myclip.embeddings import embed_text
from myclip.config import EMBEDDING_DIM


def test_full_pipeline():
    """Test: ingest → search → verify results."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db = Database(Path(tmpdir) / "test.db")
        index = SearchIndex(dim=EMBEDDING_DIM, path=f"{tmpdir}/index.faiss")

        # Ingest test fixture
        count = ingest_directory("tests/fixtures", db, index, threshold=10.0)
        assert count > 0

        # Search
        query_vec = embed_text("red background")
        results = index.search(query_vec, k=5)
        assert len(results) > 0
        assert results[0][1] > 0  # Similarity score > 0

        # Verify database
        scenes = db.get_all_scenes()
        assert len(scenes) == count
        db.close()
