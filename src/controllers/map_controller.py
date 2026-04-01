from typing import Any, Dict, Iterable, Set, Tuple

try:
    from services.layer_service import (
        build_layer_payload,
        collect_all_coordinates,
        get_route_color,
        reorder_layer_dict,
    )
    from utils.renderer import simplify_path
except ModuleNotFoundError:
    from src.services.layer_service import (
        build_layer_payload,
        collect_all_coordinates,
        get_route_color,
        reorder_layer_dict,
    )
    from src.utils.renderer import simplify_path


class MapController:
    """Encapsulates map and layer state operations independent from UI widgets."""

    def toggle_route(
        self,
        route: Dict[str, Any],
        processor: Any,
        map_widget: Any,
        active_layers: Dict[str, Dict[str, Any]],
        selected_layer_ids: Set[str],
    ) -> Tuple[Set[str], str]:
        """Toggles route layer and returns updated selection plus operation status."""
        shape_id = route["shape_id"]

        if shape_id in active_layers:
            self.remove_layer(shape_id, active_layers, selected_layer_ids)
            return set(selected_layer_ids), "removed"

        coords = processor.get_shape_coordinates(shape_id)
        if not coords:
            return set(selected_layer_ids), "missing_coords"

        if len(coords) > 500:
            coords = simplify_path(coords, epsilon=0.0001)

        color = get_route_color(route, len(active_layers))
        path_obj = map_widget.set_path(coords, color=color, width=3)
        active_layers[shape_id] = build_layer_payload(route, coords, color, path_obj, width=3)

        return {shape_id}, "added"

    def remove_layer(
        self,
        shape_id: str,
        active_layers: Dict[str, Dict[str, Any]],
        selected_layer_ids: Set[str],
    ) -> bool:
        """Removes one layer and returns True when a layer was removed."""
        if shape_id not in active_layers:
            return False

        path_obj = active_layers[shape_id].get("path_obj")
        if path_obj:
            path_obj.delete()

        del active_layers[shape_id]
        selected_layer_ids.discard(shape_id)
        return True

    def clear_all_layers(
        self,
        active_layers: Dict[str, Dict[str, Any]],
        selected_layer_ids: Set[str],
    ) -> None:
        """Clears all active layers and selection."""
        for data in active_layers.values():
            path_obj = data.get("path_obj")
            if path_obj:
                path_obj.delete()
        active_layers.clear()
        selected_layer_ids.clear()

    def fit_map_buffer(self, active_layers: Dict[str, Dict[str, Any]], map_widget: Any) -> bool:
        """Fits map view to all active coordinates. Returns False when no layers exist."""
        if not active_layers:
            return False

        all_coords = collect_all_coordinates(active_layers)
        if not all_coords:
            return False

        lats = [c[0] for c in all_coords]
        lons = [c[1] for c in all_coords]
        map_widget.fit_bounding_box((max(lats), min(lons)), (min(lats), max(lons)))
        return True

    def apply_color(
        self,
        active_layers: Dict[str, Dict[str, Any]],
        selected_layer_ids: Iterable[str],
        color: str,
    ) -> None:
        """Applies color to selected layers."""
        for sid in selected_layer_ids:
            if sid in active_layers:
                active_layers[sid]["color"] = color

    def apply_width(
        self,
        active_layers: Dict[str, Dict[str, Any]],
        selected_layer_ids: Iterable[str],
        width: int,
    ) -> None:
        """Applies width to selected layers."""
        for sid in selected_layer_ids:
            if sid in active_layers:
                active_layers[sid]["width"] = width

    def move_layer(
        self,
        active_layers: Dict[str, Dict[str, Any]],
        selected_layer_ids: Set[str],
        direction: int,
    ) -> Tuple[Dict[str, Dict[str, Any]], bool]:
        """Reorders selected layer and returns updated layers plus changed flag."""
        if not selected_layer_ids or len(selected_layer_ids) > 1:
            return active_layers, False

        sid = list(selected_layer_ids)[0]
        reordered = reorder_layer_dict(active_layers, sid, direction)
        if reordered is None:
            return active_layers, False
        return reordered, True

    def redraw_all_paths(self, active_layers: Dict[str, Dict[str, Any]], map_widget: Any) -> None:
        """Redraws all paths according to current order and style."""
        for data in active_layers.values():
            path_obj = data.get("path_obj")
            if path_obj:
                path_obj.delete()

        for data in active_layers.values():
            data["path_obj"] = map_widget.set_path(
                data["coords"], color=data["color"], width=data["width"]
            )
