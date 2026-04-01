from src.services.layer_service import (
    apply_layer_selection,
    compute_legend_rows,
    get_route_color,
    reorder_layer_dict,
)
from src.services.zoom_service import clamp_zoom, parse_zoom_value


def test_get_route_color_prefers_gtfs_color():
    route = {"route_color": "FF00AA"}
    assert get_route_color(route, active_count=2) == "#FF00AA"


def test_get_route_color_fallback_palette():
    route = {"route_color": ""}
    assert get_route_color(route, active_count=0) == "#1ABC9C"


def test_reorder_layer_dict_moves_item_down():
    layers = {
        "a": {"display_name": "A"},
        "b": {"display_name": "B"},
        "c": {"display_name": "C"},
    }
    reordered = reorder_layer_dict(layers, "b", 1)
    assert list(reordered.keys()) == ["a", "c", "b"]


def test_apply_layer_selection_shift_selects_same_short_name():
    active_layers = {
        "s1": {"short_name": "10"},
        "s2": {"short_name": "10"},
        "s3": {"short_name": "11"},
    }
    selected = apply_layer_selection(set(), active_layers, "s1", is_ctrl=False, is_shift=True)
    assert selected == {"s1", "s2"}


def test_compute_legend_rows_grouped_text():
    active_layers = {
        "s1": {
            "short_name": "10",
            "long_name": "Centro",
            "display_name": "10 - Centro (Ida)",
            "trip_headsign": "Centro",
            "color": "#123456",
        },
        "s2": {
            "short_name": "10",
            "long_name": "Centro",
            "display_name": "10 - Centro (Volta)",
            "trip_headsign": "Centro",
            "color": "#123456",
        },
    }
    rows = compute_legend_rows(active_layers)
    assert len(rows) == 1
    assert rows[0]["text"] == "10 - Centro"


def test_clamp_zoom_and_parse_zoom_value():
    assert parse_zoom_value("12,7") == 12.7
    assert parse_zoom_value("x") is None
    assert clamp_zoom(0.4) == 1.0
    assert clamp_zoom(25.8) == 19.0
    assert clamp_zoom(12.34) == 12.3
