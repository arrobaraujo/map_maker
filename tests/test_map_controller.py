from src.controllers.map_controller import MapController


class FakePath:
    def __init__(self):
        self.deleted = False

    def delete(self):
        self.deleted = True


class FakeMapWidget:
    def __init__(self):
        self.created_paths = []
        self.fit_called = False

    def set_path(self, coords, color, width):
        self.created_paths.append({"coords": coords, "color": color, "width": width})
        return FakePath()

    def fit_bounding_box(self, p1, p2):
        self.fit_called = True
        self.fit_args = (p1, p2)


class FakeProcessor:
    def __init__(self, data):
        self.data = data

    def get_shape_coordinates(self, shape_id):
        return self.data.get(shape_id, [])


def test_toggle_route_add_and_remove():
    controller = MapController()
    processor = FakeProcessor({"shape_1": [(-22.9, -43.17), (-22.91, -43.18)]})
    map_widget = FakeMapWidget()
    active_layers = {}
    selected = set()
    route = {"shape_id": "shape_1", "display_name": "R1", "route_color": "AA00BB"}

    selected, status = controller.toggle_route(route, processor, map_widget, active_layers, selected)
    assert status == "added"
    assert "shape_1" in active_layers
    assert selected == {"shape_1"}

    selected, status = controller.toggle_route(route, processor, map_widget, active_layers, selected)
    assert status == "removed"
    assert "shape_1" not in active_layers


def test_toggle_route_missing_coords():
    controller = MapController()
    processor = FakeProcessor({})
    map_widget = FakeMapWidget()
    active_layers = {}

    selected, status = controller.toggle_route(
        {"shape_id": "missing", "display_name": "R2"}, processor, map_widget, active_layers, set()
    )
    assert status == "missing_coords"
    assert active_layers == {}
    assert selected == set()


def test_fit_map_buffer_calls_widget():
    controller = MapController()
    map_widget = FakeMapWidget()
    active_layers = {
        "a": {"coords": [(-22.9, -43.17), (-22.91, -43.18)]},
        "b": {"coords": [(-22.92, -43.19)]},
    }

    did_fit = controller.fit_map_buffer(active_layers, map_widget)
    assert did_fit is True
    assert map_widget.fit_called is True


def test_move_layer_reports_when_changed():
    controller = MapController()
    layers = {
        "a": {"display_name": "A"},
        "b": {"display_name": "B"},
        "c": {"display_name": "C"},
    }

    reordered, changed = controller.move_layer(layers, {"b"}, 1)
    assert changed is True
    assert list(reordered.keys()) == ["a", "c", "b"]


def test_move_layer_reports_when_unchanged():
    controller = MapController()
    layers = {
        "a": {"display_name": "A"},
        "b": {"display_name": "B"},
    }

    reordered, changed = controller.move_layer(layers, set(), 1)
    assert changed is False
    assert reordered == layers
