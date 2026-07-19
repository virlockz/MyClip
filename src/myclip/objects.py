from pathlib import Path

from ultralytics import YOLO

_model = None


def _get_model():
    global _model
    if _model is None:
        _model = YOLO("yolo11n.pt")
    return _model


def detect_objects(image_path: str | Path) -> list[str]:
    """Detect objects in an image using YOLO.

    Args:
        image_path: Path to image file.

    Returns:
        List of detected class label strings.
    """
    model = _get_model()
    results = model(str(image_path), verbose=False)

    labels = []
    for result in results:
        if result.boxes is not None:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                label = result.names[cls_id]
                if label not in labels:
                    labels.append(label)

    return labels
