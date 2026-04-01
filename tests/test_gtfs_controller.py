from src.controllers.gtfs_controller import GTFSController


class FakeProcessor:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


def test_create_processor_closes_old_processor():
    created = []

    def fake_factory(path):
        created.append(path)
        return {"path": path}

    controller = GTFSController(processor_factory=fake_factory)
    old = FakeProcessor()

    new_processor = controller.create_processor("sample.zip", old)

    assert old.closed is True
    assert new_processor == {"path": "sample.zip"}
    assert created == ["sample.zip"]


def test_load_async_success_calls_on_loaded():
    controller = GTFSController(processor_factory=lambda path: {"path": path})
    loaded = []
    errors = []

    thread = controller.load_async(
        file_path="ok.zip",
        old_processor=None,
        on_loaded=lambda p: loaded.append(p),
        on_error=lambda e: errors.append(e),
    )
    thread.join(timeout=2)

    assert loaded == [{"path": "ok.zip"}]
    assert errors == []


def test_load_async_error_calls_on_error():
    def failing_factory(_):
        raise ValueError("bad file")

    controller = GTFSController(processor_factory=failing_factory)
    loaded = []
    errors = []

    thread = controller.load_async(
        file_path="bad.zip",
        old_processor=None,
        on_loaded=lambda p: loaded.append(p),
        on_error=lambda e: errors.append(e),
    )
    thread.join(timeout=2)

    assert loaded == []
    assert errors == ["bad file"]
