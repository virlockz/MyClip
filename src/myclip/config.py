from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "myclip.db"
FAISS_PATH = DATA_DIR / "scene_index.faiss"
THUMBNAILS_DIR = DATA_DIR / "thumbnails"
CLIPS_DIR = DATA_DIR / "clips"

# Scene detection defaults
DEFAULT_THRESHOLD = 27.0

# CLIP defaults
CLIP_MODEL = "ViT-B-32"
CLIP_PRETRAINED = "laion2b_s34b_b79k"
EMBEDDING_DIM = 512

# Dedup defaults
DEDUP_THRESHOLD = 2.0
DEDUP_THUMB_SIZE = 16
