from myclip.scene_detect import detect_scenes, SceneBoundary


def test_detect_scenes_returns_list():
    scenes = detect_scenes("tests/fixtures/sample_video.mp4")
    assert isinstance(scenes, list)
    assert len(scenes) >= 2  # At least 2 scenes in our 3-color video


def test_scene_boundary_has_correct_fields():
    scenes = detect_scenes("tests/fixtures/sample_video.mp4")
    assert len(scenes) > 0
    scene = scenes[0]
    assert hasattr(scene, "start_sec")
    assert hasattr(scene, "end_sec")
    assert scene.start_sec >= 0
    assert scene.end_sec > scene.start_sec


def test_scene_boundaries_are_sorted():
    scenes = detect_scenes("tests/fixtures/sample_video.mp4")
    for i in range(len(scenes) - 1):
        assert scenes[i].end_sec <= scenes[i + 1].start_sec


def test_threshold_affects_scene_count():
    low = detect_scenes("tests/fixtures/sample_video.mp4", threshold=10.0)
    high = detect_scenes("tests/fixtures/sample_video.mp4", threshold=50.0)
    assert len(low) >= len(high)  # Lower threshold = more scenes
