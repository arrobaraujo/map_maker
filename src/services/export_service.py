from typing import Any, Dict, Iterable, List, Tuple

import geopandas as gpd
from shapely.geometry import LineString
from tkintermapview import decimal_to_osm


def build_gdf_features(active_layers: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Builds GeoDataFrame-compatible features from active layers."""
    features: List[Dict[str, Any]] = []
    for shape_id, data in active_layers.items():
        coords_lonlat = [(c[1], c[0]) for c in data.get("coords", [])]
        features.append(
            {
                "geometry": LineString(coords_lonlat),
                "shape_id": shape_id,
                "name": data.get("display_name", ""),
                "color": data.get("color", "#000000"),
            }
        )
    return features


def export_vector_file(active_layers: Dict[str, Dict[str, Any]], file_path: str) -> None:
    """Exports active layers as GeoPackage or Shapefile based on file extension."""
    features = build_gdf_features(active_layers)
    gdf = gpd.GeoDataFrame(features, crs="EPSG:4326")
    driver = "ESRI Shapefile" if file_path.lower().endswith(".shp") else "GPKG"
    gdf.to_file(file_path, driver=driver)


def build_kml(active_layers: Dict[str, Dict[str, Any]]) -> str:
    """Builds KML content for active layers."""
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<kml xmlns="http://www.opengis.net/kml/2.2">',
        '<Document>',
    ]

    for data in active_layers.values():
        color_hex = str(data.get("color", "#000000")).lstrip("#")
        if len(color_hex) != 6:
            color_hex = "000000"
        kml_color = f"ff{color_hex[4:6]}{color_hex[2:4]}{color_hex[0:2]}"

        coords = " ".join([f"{c[1]},{c[0]},0" for c in data.get("coords", [])])

        lines.extend(
            [
                "  <Placemark>",
                f"    <name>{data.get('display_name', '')}</name>",
                f"    <Style><LineStyle><color>{kml_color}</color><width>{data.get('width', 3)}</width></LineStyle></Style>",
                "    <LineString>",
                "      <coordinates>",
                f"        {coords}",
                "      </coordinates>",
                "    </LineString>",
                "  </Placemark>",
            ]
        )

    lines.extend(["</Document>", "</kml>"])
    return "\n".join(lines)


def save_kml(active_layers: Dict[str, Dict[str, Any]], file_path: str) -> None:
    """Writes KML content to disk for active layers."""
    kml_content = build_kml(active_layers)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(kml_content)


def project_coords_to_svg_points(
    coords: Iterable[Tuple[float, float]],
    width: float,
    height: float,
    ul_x: float,
    ul_y: float,
    tile_w: float,
    tile_h: float,
    zoom: int,
) -> List[str]:
    """Projects lat/lon coordinates into SVG viewport points."""
    points: List[str] = []
    for lat, lon in coords:
        tx, ty = decimal_to_osm(lat, lon, zoom)
        px = ((tx - ul_x) / tile_w) * width
        py = ((ty - ul_y) / tile_h) * height
        points.append(f"{px},{py}")
    return points


def build_svg(
    active_layers: Dict[str, Dict[str, Any]],
    width: int,
    height: int,
    scale: float,
    ul_x: float,
    ul_y: float,
    tile_w: float,
    tile_h: float,
    zoom: int,
    transparent_background: bool,
) -> str:
    """Builds SVG content from active layers and map projection context."""
    lines = [
        f'<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg width="{width*scale}" height="{height*scale}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">',
    ]

    if not transparent_background:
        lines.append('  <rect width="100%" height="100%" fill="white" />')

    for data in active_layers.values():
        points = project_coords_to_svg_points(
            data.get("coords", []), width, height, ul_x, ul_y, tile_w, tile_h, zoom
        )
        path_data = "L".join(points)
        if path_data:
            lines.append(
                f'  <path d="M{path_data}" fill="none" stroke="{data.get("color", "#000000")}" stroke-width="{data.get("width", 3)}" stroke-linejoin="round" />'
            )

    lines.append("</svg>")
    return "\n".join(lines)


def save_svg(
    active_layers: Dict[str, Dict[str, Any]],
    file_path: str,
    width: int,
    height: int,
    scale: float,
    ul_x: float,
    ul_y: float,
    tile_w: float,
    tile_h: float,
    zoom: int,
    transparent_background: bool,
) -> None:
    """Writes SVG content to disk."""
    svg_content = build_svg(
        active_layers,
        width,
        height,
        scale,
        ul_x,
        ul_y,
        tile_w,
        tile_h,
        zoom,
        transparent_background,
    )
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
