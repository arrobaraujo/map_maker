from typing import Optional


def clamp_zoom(value: float, min_zoom: float = 1.0, max_zoom: float = 19.0) -> float:
    """Clamps zoom to supported limits and rounds to one decimal place."""
    return round(max(min_zoom, min(max_zoom, value)), 1)


def parse_zoom_value(raw_value: str) -> Optional[float]:
    """Parses localized zoom text. Returns None for invalid values."""
    try:
        return float(raw_value.replace(",", ".").strip())
    except (TypeError, ValueError):
        return None
