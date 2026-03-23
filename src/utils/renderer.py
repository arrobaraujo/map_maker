import logging
from typing import List, Tuple, Dict, Any
from PIL import Image, ImageDraw, ImageFont
from tkintermapview import decimal_to_osm

logger = logging.getLogger(__name__)

def render_transparent_map(
    width: int, 
    height: int, 
    scale: float, 
    active_layers: Dict[str, Dict[str, Any]], 
    map_widget: Any,
    show_legend: bool
) -> Image.Image:
    """
    Renders a map with a transparent background using manual coordinate projection.

    Args:
        width: Canvas width.
        height: Canvas height.
        scale: DPI scale factor.
        active_layers: Dictionary of layers to render.
        map_widget: The TkinterMapView instance for projection parameters.
        show_legend: Whether to include the legend.

    Returns:
        A PIL Image object.
    """
    logger.info(f"Rendering transparent map at size {width}x{height} with scale {scale}")
    
    img_w, img_h = int(width * scale), int(height * scale)
    image = Image.new("RGBA", (img_w, img_h), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)

    # Get tile dimensions for manual projection
    tile_w = map_widget.lower_right_tile_pos[0] - map_widget.upper_left_tile_pos[0]
    tile_h = map_widget.lower_right_tile_pos[1] - map_widget.upper_left_tile_pos[1]
    ul_x, ul_y = map_widget.upper_left_tile_pos
    zoom = round(map_widget.zoom)

    # Render paths
    for data in active_layers.values():
        points = []
        for lat, lon in data['coords']:
            # Manual Lat/Lon -> Pixel conversion
            tx, ty = decimal_to_osm(lat, lon, zoom)
            px = ((tx - ul_x) / tile_w) * width
            py = ((ty - ul_y) / tile_h) * height
            points.append((px * scale, py * scale))
        
        if len(points) > 1:
            draw.line(points, fill=data['color'], width=int(data['width'] * scale), joint="curve")
    
    # Render legend if requested
    if show_legend and active_layers:
        _draw_legend(draw, active_layers, img_w, img_h, scale)
        
    return image

def _draw_legend(draw: ImageDraw.Draw, active_layers: Dict[str, Dict[str, Any]], img_w: int, img_h: int, scale: float):
    """Internal helper to draw the legend on the image."""
    lw, lh = 400 * scale, (60 + len(active_layers) * 30) * scale
    lx, ly = 20 * scale, img_h - lh - 20 * scale
    
    # Draw legend box
    draw.rectangle([lx, ly, lx + lw, ly + lh], fill="white", outline="gray")
    
    try:
        font = ImageFont.truetype("arial.ttf", int(14 * scale))
    except Exception:
        font = ImageFont.load_default()
        
    curr_y = ly + 15 * scale
    # Grouping logic to match original behavior
    groups = {}
    for data in active_layers.values():
        sn = data['short_name']
        if sn not in groups: groups[sn] = []
        groups[sn].append(data)

    for sn, layers in groups.items():
        color_groups = {}
        for l in layers:
            c = l['color']
            if c not in color_groups: color_groups[c] = []
            color_groups[c].append(l)
        
        for color, sub_layers in color_groups.items():
            layer0 = sub_layers[0]
            is_circular = "circular" in str(layer0.get('trip_headsign', '')).lower()
            
            if is_circular:
                legend_text = f"{sn} - {layer0.get('long_name', '')}".strip(" - ")
            elif len(sub_layers) > 1:
                legend_text = f"{sn} - {layer0.get('long_name', '')}".strip(" - ")
            else:
                legend_text = layer0['display_name']
                
            # Draw color sample
            draw.rectangle([lx + 15 * scale, curr_y, lx + 35 * scale, curr_y + 20 * scale], fill=color)
            # Draw text
            draw.text((lx + 45 * scale, curr_y), legend_text, fill="black", font=font)
            curr_y += 30 * scale
