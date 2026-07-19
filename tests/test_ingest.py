import tempfile
from pathlib import Path

from myclip.ingest import ingest_directory
from myclip.database import Database
from myclip.search import SearchIndex
from myclip.config import EMBEDDING_DIM


def test_ingest_directory():
    with tempfile.TemporaryDirectory() as tmpdir:
        db = Database(Path(tmpdir) / "test.db")
        index = SearchIndex(dim=EMBEDDING_DIM, path=f"{tmpdir}/index.faiss")
        count = ingest_directory("tests/fixtures", db, index)
        assert count > 0
        scenes = db.get_all_scenes()
        assert len(scenes) == count
        assert index.size > 0
        db.close()
