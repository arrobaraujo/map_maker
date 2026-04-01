from src.services.export_service import build_kml, build_svg


def _sample_layers():
    return {
        "shape_1": {
            "display_name": "10 - Centro",
            "color": "#FF0000",
            "width": 3,
            "coords": [(-22.9, -43.17), (-22.91, -43.18)],
        }
    }


def test_build_kml_contains_layer_name_and_coordinates():
    kml = build_kml(_sample_layers())
    assert "<name>10 - Centro</name>" in kml
    assert "-43.17,-22.9,0" in kml
    assert "<kml" in kml


def test_build_svg_contains_path():
    svg = build_svg(
        active_layers=_sample_layers(),
        width=1000,
        height=800,
        scale=1.0,
        ul_x=0,
        ul_y=0,
        tile_w=1,
        tile_h=1,
        zoom=12,
        transparent_background=False,
    )
    assert "<svg" in svg
    assert "<path d=\"M" in svg
