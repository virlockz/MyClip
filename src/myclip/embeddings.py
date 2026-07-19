from pathlib import Path

import numpy as np
import torch
import open_clip

from myclip.config import CLIP_MODEL, CLIP_PRETRAINED, EMBEDDING_DIM

# Lazy-loaded model and tokenizer
_model = None
_preprocess = None
_tokenizer = None


def _get_model():
    global _model, _preprocess, _tokenizer
    if _model is None:
        _model, _, _preprocess = open_clip.create_model_and_transforms(
            CLIP_MODEL, pretrained=CLIP_PRETRAINED
        )
        _model.eval()
        _tokenizer = open_clip.get_tokenizer(CLIP_MODEL)
    return _model, _preprocess, _tokenizer


def embed_image(image_path: str | Path) -> np.ndarray:
    """Generate CLIP embedding for an image file.

    Args:
        image_path: Path to image JPEG/PNG.

    Returns:
        L2-normalized 512-dim float32 vector.
    """
    from PIL import Image

    model, preprocess, _ = _get_model()
    img = Image.open(image_path).convert("RGB")
    tensor = preprocess(img).unsqueeze(0)

    with torch.no_grad():
        features = model.encode_image(tensor)
        features /= features.norm(dim=-1, keepdim=True)

    return features.squeeze().numpy().astype(np.float32)


def embed_text(text: str) -> np.ndarray:
    """Generate CLIP embedding for a text query.

    Args:
        text: Natural language description.

    Returns:
        L2-normalized 512-dim float32 vector.
    """
    model, _, tokenizer = _get_model()
    tokens = tokenizer([text])

    with torch.no_grad():
        features = model.encode_text(tokens)
        features /= features.norm(dim=-1, keepdim=True)

    return features.squeeze().numpy().astype(np.float32)


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Compute cosine similarity between two vectors."""
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
