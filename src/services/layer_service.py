from typing import Any, Dict, Iterable, List, Optional, Set

DEFAULT_LAYER_COLORS = (
    "#1ABC9C",
    "#E74C3C",
    "#3498DB",
    "#F1C40F",
    "#9B59B6",
    "#E67E22",
    "#2ECC71",
)


def get_route_color(route: Dict[str, Any], active_count: int) -> str:
    """Returns GTFS route color when available, otherwise rotates a default palette."""
    gtfs_color = str(route.get("route_color", "")).strip("#").strip()
    if len(gtfs_color) == 6:
        return f"#{gtfs_color}"
    return DEFAULT_LAYER_COLORS[active_count % len(DEFAULT_LAYER_COLORS)]


def build_layer_payload(
    route: Dict[str, Any],
    coords: Iterable[Any],
    color: str,
    path_obj: Any,
    width: int = 3,
) -> Dict[str, Any]:
    """Builds standardized layer metadata used by map rendering and exports."""
    return {
        "shape_id": route["shape_id"],
        "display_name": route["display_name"],
        "short_name": route.get("short_name", ""),
        "long_name": route.get("long_name", ""),
        "direction": route.get("direction", ""),
        "trip_headsign": route.get("trip_headsign", ""),
        "path_obj": path_obj,
        "color": color,
        "width": width,
        "coords": list(coords),
    }


def collect_all_coordinates(active_layers: Dict[str, Dict[str, Any]]) -> List[Any]:
    """Returns all coordinates from active layers preserving layer order."""
    all_coords: List[Any] = []
    for layer in active_layers.values():
        all_coords.extend(layer.get("coords", []))
    return all_coords


def reorder_layer_dict(
    active_layers: Dict[str, Dict[str, Any]], selected_shape_id: str, direction: int
) -> Optional[Dict[str, Dict[str, Any]]]:
    """Returns reordered layers dict after moving selected layer up/down, or None if unchanged."""
    keys = list(active_layers.keys())
    if selected_shape_id not in active_layers:
        return None

    idx = keys.index(selected_shape_id)
    new_idx = idx + direction
    if not (0 <= new_idx < len(keys)):
        return None

    keys[idx], keys[new_idx] = keys[new_idx], keys[idx]
    return {k: active_layers[k] for k in keys}


def apply_layer_selection(
    selected_layer_ids: Set[str],
    active_layers: Dict[str, Dict[str, Any]],
    shape_id: str,
    is_ctrl: bool,
    is_shift: bool,
) -> Set[str]:
    """Computes next selected layer set based on click modifiers."""
    if shape_id not in active_layers:
        return set(selected_layer_ids)

    next_selection = set(selected_layer_ids)

    if is_shift:
        target_short_name = active_layers[shape_id].get("short_name", "")
        for sid, data in active_layers.items():
            if data.get("short_name", "") == target_short_name:
                next_selection.add(sid)
        return next_selection

    if is_ctrl:
        if shape_id in next_selection:
            next_selection.remove(shape_id)
        else:
            next_selection.add(shape_id)
        return next_selection

    return {shape_id}


def compute_legend_rows(active_layers: Dict[str, Dict[str, Any]]) -> List[Dict[str, str]]:
    """Builds flattened legend rows preserving grouping rules used by the UI."""
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for data in active_layers.values():
        short_name = data.get("short_name", "")
        groups.setdefault(short_name, []).append(data)

    rows: List[Dict[str, str]] = []
    for short_name, layers in groups.items():
        color_groups: Dict[str, List[Dict[str, Any]]] = {}
        for layer in layers:
            color = layer.get("color", "#000000")
            color_groups.setdefault(color, []).append(layer)

        for color, sub_layers in color_groups.items():
            layer0 = sub_layers[0]
            is_circular = "circular" in str(layer0.get("trip_headsign", "")).lower()
            if is_circular or len(sub_layers) > 1:
                text = f"{short_name} - {layer0.get('long_name', '')}".strip(" - ")
            else:
                text = layer0.get("display_name", "")

            rows.append({"color": color, "text": text})

    return rows
