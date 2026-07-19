import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

from myclip.embeddings import embed_image, embed_text, cosine_similarity


def test_embed_image_returns_vector():
    # Create a temporary image for testing
    with tempfile.TemporaryDirectory() as tmpdir:
        img = Image.new("RGB", (100, 100), color="red")
        img_path = Path(tmpdir) / "test.jpg"
        img.save(img_path)
        vec = embed_image(img_path)
        assert isinstance(vec, np.ndarray)
        assert vec.shape == (512,)


def test_embed_text_returns_vector():
    vec = embed_text("a person sitting in an office")
    assert isinstance(vec, np.ndarray)
    assert vec.shape == (512,)


def test_cosine_similarity_range():
    a = embed_text("interrogation room")
    b = embed_text("someone being questioned")
    sim = cosine_similarity(a, b)
    assert -1.0 <= sim <= 1.0


def test_similar_text_higher_similarity():
    a = embed_text("interrogation room")
    b = embed_text("someone being questioned")
    c = embed_text("a red car driving fast")
    sim_related = cosine_similarity(a, b)
    sim_unrelated = cosine_similarity(a, c)
    assert sim_related > sim_unrelated
