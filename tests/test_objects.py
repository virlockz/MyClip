from myclip.objects import detect_objects


def test_detect_objects_returns_list():
    objects = detect_objects("tests/fixtures/sample_video.mp4")
    assert isinstance(objects, list)


def test_detect_objects_returns_strings():
    objects = detect_objects("tests/fixtures/sample_video.mp4")
    for obj in objects:
        assert isinstance(obj, str)
