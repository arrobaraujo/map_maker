import customtkinter as ctk
from tkinter import filedialog, messagebox, colorchooser
import sys
import os
import time
import logging
from PIL import Image, ImageGrab
from typing import List, Dict, Any, Optional

# Add the src/ directory to the path to ensure imports work correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from processor import GTFSProcessor
from utils.renderer import render_transparent_map
from services.layer_service import (
    apply_layer_selection,
    compute_legend_rows,
)
from services.zoom_service import clamp_zoom, parse_zoom_value
from services.export_service import export_vector_file, save_kml, save_svg
from ui.ui_builder import build_main_ui
from controllers.map_controller import MapController
from controllers.gtfs_controller import GTFSController

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

APP_VERSION = "1.4.0"

# High DPI awareness for Windows
try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

class GTFSMapApp(ctk.CTk):
    """
    Main Application class for GTFS Map Maker.
    Handles UI, user interactions, and map display.
    """
    def __init__(self):
        super().__init__()

        self.title(f"GTFS Map Maker v{APP_VERSION}")
        self.geometry("1400x900")
        
        # Open maximized on Windows (delayed to ensure it stays)
        self.after(0, lambda: self._maximize_window())

        # Application State
        self.processor: Optional[GTFSProcessor] = None
        self.all_routes: List[Dict] = []
        self.filtered_routes: List[Dict] = []
        self.active_layers: Dict[str, Dict[str, Any]] = {}
        self.selected_layer_ids: set[str] = set()
        self.map_controller = MapController()
        self.gtfs_controller = GTFSController()

        # Configuration
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        # Tile Cache Directory (Offline Database)
        # Assuming we keep it in the root for now
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.tile_cache_dir = os.path.join(root_dir, "map_tiles_cache")
        os.makedirs(self.tile_cache_dir, exist_ok=True)
        self.db_path = os.path.join(self.tile_cache_dir, "offline_tiles.db")

        self.setup_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        logger.info("Application initialized.")

    def _on_close(self):
        """Ensures resources are released before the app exits."""
        try:
            if self.processor is not None:
                self.processor.close()
        except Exception:
            logger.exception("Failed to close processor cleanly")
        self.destroy()

    def setup_ui(self):
        """Sets up the graphical user interface components."""
        build_main_ui(self)

    def load_gtfs(self):
        """Opens a file dialog to load a GTFS ZIP file in a separate thread."""
        file_path = filedialog.askopenfilename(filetypes=[("GTFS ZIP", "*.zip")])
        if file_path:
            # Show loading indicator
            self.load_button.configure(state="disabled", text="⌛ Carregando...")
            self.root_loading_label = ctk.CTkLabel(self.sidebar, text="Processando dados GTFS...\nIsso pode demorar um pouco.", 
                                                text_color="#E67E22", font=ctk.CTkFont(size=12, slant="italic"))
            self.root_loading_label.grid(row=1, column=0, pady=(65, 0))
            
            self.gtfs_controller.load_async(
                file_path=file_path,
                old_processor=self.processor,
                on_loaded=lambda new_processor: self.after(0, lambda: self._on_gtfs_loaded(new_processor)),
                on_error=lambda error_msg: self.after(0, lambda: self._on_gtfs_error(error_msg)),
            )

    def _on_gtfs_loaded(self, processor):
        """Callback for when GTFS loading is complete."""
        self.processor = processor
        self.load_button.configure(state="normal", text="📁 Carregar GTFS (.zip)")
        if hasattr(self, 'root_loading_label'):
            self.root_loading_label.destroy()
            
        self.refresh_route_list()
        messagebox.showinfo("Sucesso", f"GTFS carregado!\nLinhas disponíveis para seleção.")

    def _on_gtfs_error(self, error_msg):
        """Callback for when GTFS loading fails."""
        self.load_button.configure(state="normal", text="📁 Carregar GTFS (.zip)")
        if hasattr(self, 'root_loading_label'):
            self.root_loading_label.destroy()
        messagebox.showerror("Erro", f"Falha ao carregar GTFS: {error_msg}")

    def refresh_route_list(self):
        """Refreshes the sidebar list of available routes with virtual scrolling."""
        if not self.processor: return
        self.all_routes = self.processor.get_route_list()
        self.filtered_routes = self.all_routes.copy()
        
        # Clear existing
        for widget in self.route_listbox.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.route_listbox, text="Linhas Disponíveis", 
                     font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(5, 5))
            
        # UI Layout: [ Virtual Frame (Buttons) | Scrollbar ]
        self.virtual_frame = ctk.CTkFrame(self.route_listbox, fg_color="transparent")
        self.virtual_frame.pack(side="left", fill="both", expand=True)
        
        self.route_scrollbar = ctk.CTkScrollbar(self.route_listbox, command=self._on_scrollbar_move)
        self.route_scrollbar.pack(side="right", fill="y")
        
        # Setup Virtual Scroll parameters
        self.item_height = 36
        self.scroll_offset = 0
        
        # Calculate visible items based on frame height
        self.update() # Force layout to get height
        available_height = self.route_listbox.winfo_height() - 40 # Subtract label space
        self.visible_items = max(5, (available_height // self.item_height) + 1)
        
        # Create button pool
        self.button_pool = []
        for i in range(self.visible_items):
            btn = ctk.CTkButton(self.virtual_frame, text="", height=self.item_height-4, anchor="w", fg_color="transparent")
            btn.pack(fill="x", padx=5, pady=2)
            btn.bind("<MouseWheel>", self._on_mousewheel)
            self.button_pool.append(btn)
            
        self.virtual_frame.bind("<MouseWheel>", self._on_mousewheel)
        self._update_virtual_scroll()

    def _on_scrollbar_move(self, action, value, unit=None):
        """Manually handles scrollbar actions to update the virtual list."""
        total_items = len(self.filtered_routes)
        if action == "moveto":
            self.scroll_offset = int(float(value) * total_items)
        elif action == "scroll":
            delta = int(value)
            self.scroll_offset += delta
            
        self._update_virtual_scroll()

    def _on_mousewheel(self, event):
        """Handles mouse wheel by shifting the scroll offset."""
        delta = -1 if event.delta > 0 else 1
        self.scroll_offset += delta
        self._update_virtual_scroll()

    def _update_virtual_scroll(self, event=None):
        """Refreshes button content based on self.scroll_offset."""
        if not hasattr(self, 'filtered_routes'): return
        
        total_items = len(self.filtered_routes)
        # Constrain offset
        max_offset = max(0, total_items - self.visible_items)
        self.scroll_offset = max(0, min(self.scroll_offset, max_offset))
        
        # Update scrollbar position
        if total_items > 0:
            start = self.scroll_offset / total_items
            end = (self.scroll_offset + self.visible_items) / total_items
            self.route_scrollbar.set(start, end)
        
        for i, btn in enumerate(self.button_pool):
            route_idx = self.scroll_offset + i
            if route_idx < total_items:
                route = self.filtered_routes[route_idx]
                is_active = route['shape_id'] in self.active_layers
                
                btn.configure(
                    text=route['display_name'],
                    fg_color="#34495E" if is_active else "transparent",
                    command=lambda r=route: self.toggle_route(r),
                    state="normal"
                )
            else:
                btn.configure(text="", state="disabled", fg_color="transparent")

    def filter_routes(self, event=None):
        """Filters the route list and resets virtual scroll."""
        if not self.processor: return
        query = self.search_entry.get().lower()
        self.filtered_routes = [r for r in self.all_routes if query in r['display_name'].lower()]
        self.scroll_offset = 0
        self._update_virtual_scroll()

    def toggle_route(self, route: Dict):
        """Add or removes a route from the map."""
        selected_ids, status = self.map_controller.toggle_route(
            route,
            self.processor,
            self.map_widget,
            self.active_layers,
            self.selected_layer_ids,
        )
        if status == "missing_coords":
            messagebox.showwarning("Aviso", f"Sem coordenadas para {route['shape_id']}")
            return

        self.selected_layer_ids = selected_ids
        
        self.refresh_layer_list()
        self._update_virtual_scroll() # Update pool colors
        self.redraw_all_paths()
        self.update_legend()

    def _remove_layer(self, shape_id: str):
        """Internal helper to remove a specific layer."""
        if self.map_controller.remove_layer(shape_id, self.active_layers, self.selected_layer_ids):
            self.refresh_layer_list()
            self.filter_routes()
            self.redraw_all_paths()
            self.update_legend()

    def clear_all_layers(self):
        """Removes all layers from the map."""
        self.map_controller.clear_all_layers(self.active_layers, self.selected_layer_ids)
        self.refresh_layer_list()
        self.filter_routes()
        self.update_legend()

    def fit_map_buffer(self):
        """Adjusts the map zoom and position to fit all active layers."""
        did_fit = self.map_controller.fit_map_buffer(self.active_layers, self.map_widget)
        if did_fit:
            self.after(500, self.sync_zoom_from_map)

    def adjust_zoom(self, delta):
        """Increments or decrements the zoom by delta."""
        current_zoom = float(self.map_widget.zoom)
        self.map_widget.set_zoom(clamp_zoom(current_zoom + delta))
        self.after(200, self.sync_zoom_from_map)

    def update_zoom_from_entry(self):
        """Updates the map zoom based on the entry field value."""
        val = parse_zoom_value(self.zoom_entry.get())
        if val is not None:
            self.map_widget.set_zoom(clamp_zoom(val))
            self.after(200, self.sync_zoom_from_map)
        else:
            self.sync_zoom_from_map()

    def sync_zoom_from_map(self):
        """Synchronizes the entry field with the current map zoom level."""
        current_zoom = float(self.map_widget.zoom)
        self.zoom_entry.delete(0, "end")
        self.zoom_entry.insert(0, f"{current_zoom:.1f}")

    def refresh_layer_list(self):
        """Updates the active layers list in the sidebar."""
        for widget in self.layer_listbox.winfo_children(): widget.destroy()
        for shape_id, data in self.active_layers.items():
            is_sel = shape_id in self.selected_layer_ids
            row = ctk.CTkFrame(self.layer_listbox, fg_color="transparent")
            row.pack(fill="x", padx=2, pady=2)
            
            btn = ctk.CTkButton(row, text=data['display_name'],
                               fg_color="#2980B9" if is_sel else "transparent",
                               command=None) # We'll bind the event manually
            btn.pack(side="left", fill="x", expand=True, padx=(0, 2))
            btn.bind("<Button-1>", lambda e, s=shape_id: self.select_layer(s, e))
            
            ctk.CTkButton(row, text="✕", width=30, height=32, command=lambda s=shape_id: self._remove_layer(s)).pack(side="right")

    def select_layer(self, shape_id: str, event=None):
        """Sets a layer as the currently selected one for styling. 
        - Click: Select one
        - Ctrl + Click: Toggle selection
        - Shift + Click: Select all trips of the same line
        """
        if shape_id not in self.active_layers: return

        # Detect modifiers
        is_ctrl = False
        is_shift = False
        if event:
            is_ctrl = (event.state & 0x0004) or (sys.platform == "darwin" and event.state & 0x0008)
            is_shift = (event.state & 0x0001)

        self.selected_layer_ids = apply_layer_selection(
            self.selected_layer_ids,
            self.active_layers,
            shape_id,
            is_ctrl=bool(is_ctrl),
            is_shift=bool(is_shift),
        )

        # Update UI sliders with the first selected layer's values
        if self.selected_layer_ids:
            first_id = list(self.selected_layer_ids)[0]
            data = self.active_layers[first_id]
            self.width_slider.set(data['width'])
            self.width_label.configure(text=f"Espessura: {int(data['width'])}")
        
        self.refresh_layer_list()

    def choose_color(self):
        """Opens a color chooser for the selected layers."""
        if not self.selected_layer_ids: return
        color = colorchooser.askcolor(title="Escolha a cor da linha")[1]
        if color:
            self.map_controller.apply_color(self.active_layers, self.selected_layer_ids, color)
            self.redraw_all_paths()
            self.update_legend()

    def update_style(self, value):
        """Updates the line width for the selected layers."""
        if not self.selected_layer_ids: return
        self.map_controller.apply_width(self.active_layers, self.selected_layer_ids, int(value))
        self.width_label.configure(text=f"Espessura: {int(value)}")
        self.redraw_all_paths()

    def move_layer(self, direction: int):
        """Changes the rendering order of layers."""
        self.active_layers, changed = self.map_controller.move_layer(
            self.active_layers, self.selected_layer_ids, direction
        )
        if changed:
            self.redraw_all_paths()
            self.refresh_layer_list()
            self.update_legend()

    def redraw_all_paths(self):
        """Redraws all paths on the map widgets according to their order and style."""
        self.map_controller.redraw_all_paths(self.active_layers, self.map_widget)

    def toggle_legend_ui(self):
        """Shows or hides the map legend overlay."""
        if self.legend_switch.get(): self.update_legend()
        else: self.legend_frame.place_forget()

    def update_legend(self):
        """Redraws the floating legend box."""
        for widget in self.legend_frame.winfo_children(): widget.destroy()
        if not self.legend_switch.get() or not self.active_layers:
            self.legend_frame.place_forget()
            return

        self.legend_frame.place(relx=0.02, rely=0.98, anchor="sw")
        self.legend_frame.lift()
        
        for legend_row in compute_legend_rows(self.active_layers):
            row = ctk.CTkFrame(self.legend_frame, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=5)
            ctk.CTkLabel(row, text=" ■ ", text_color=legend_row['color'], font=ctk.CTkFont(size=24)).pack(side="left")
            ctk.CTkLabel(row, text=legend_row['text'], font=ctk.CTkFont(size=13), text_color="black").pack(side="left", padx=5)

    def export_sig(self):
        """Exports active layers as GeoPackage, Shapefile, or KML."""
        if not self.active_layers: return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".gpkg", 
            filetypes=[("GeoPackage", "*.gpkg"), ("Shapefile", "*.shp"), ("KML", "*.kml")]
        )
        if not file_path: return
        
        try:
            if file_path.lower().endswith(".kml"):
                save_kml(self.active_layers, file_path)
            else:
                export_vector_file(self.active_layers, file_path)
            
            messagebox.showinfo("Sucesso", "Exportado com sucesso!")
        except Exception as e: 
            logger.exception("GIS export failed")
            messagebox.showerror("Erro", str(e))

    def change_basemap(self, choice: str):
        """Changes the tile server based on user choice."""
        if choice == "OpenStreetMap":
            self.map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")
        elif choice == "Google Normal":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga")
        elif choice in ["Esri Light", "Esri Dark"]:
            url = "World_Light_Gray_Base" if "Light" in choice else "World_Dark_Gray_Base"
            self.map_widget.set_tile_server(f"https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/{url}/MapServer/tile/{{z}}/{{y}}/{{x}}")
        elif choice in ["Carto Light", "Carto Dark"]:
            url = "light_all" if "Light" in choice else "dark_all"
            self.map_widget.set_tile_server(f"https://a.basemaps.cartocdn.com/{url}/{{z}}/{{x}}/{{y}}.png")
        elif choice == "Transparent":
            self.map_widget.set_tile_server("about:blank")
            self.map_widget.canvas.configure(bg="#00FF01") # Green screen-ish for transparency

    def save_map(self):
        """Saves the current map as an image (PNG/PDF/SVG)."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png", 
            filetypes=[("PNG", "*.png"), ("PDF", "*.pdf"), ("SVG", "*.svg")]
        )
        if not file_path: return
        try:
            try: dpi = int(self.dpi_entry.get())
            except: dpi = 300
            scale = dpi / 96.0

            if file_path.lower().endswith(".svg"):
                self._save_svg(file_path, scale)
            elif self.basemap_menu.get() == "Transparent" and file_path.lower().endswith(".png"):
                # Use decoupled rendering logic for high-quality transparent export
                image = render_transparent_map(
                    self.map_container.winfo_width(),
                    self.map_container.winfo_height(),
                    scale,
                    self.active_layers,
                    self.map_widget,
                    self.legend_switch.get()
                )
                image.save(file_path, dpi=(dpi, dpi))
            else:
                # Standard screen capture
                self.map_widget.canvas.itemconfig("button", state='hidden')
                self.update()
                time.sleep(0.5)
                x, y, w, h = self.map_container.winfo_rootx(), self.map_container.winfo_rooty(), self.map_container.winfo_width(), self.map_container.winfo_height()
                image = ImageGrab.grab(bbox=(x, y, x + w, y + h), all_screens=True)
                if scale > 1.1: 
                    image = image.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
                
                if file_path.endswith(".pdf"): 
                    image.convert("RGB").save(file_path, resolution=float(dpi))
                else: 
                    image.save(file_path, dpi=(dpi, dpi))
            
            messagebox.showinfo("Sucesso", "Mapa salvo com sucesso!")
        except Exception as e: 
            logger.exception("Save map failed")
            messagebox.showerror("Erro", str(e))
        finally:
            self.map_widget.canvas.itemconfig("button", state='normal')

    def _save_svg(self, file_path: str, scale: float):
        """Saves active layers as a vector SVG file."""
        width = self.map_container.winfo_width()
        height = self.map_container.winfo_height()

        tile_w = self.map_widget.lower_right_tile_pos[0] - self.map_widget.upper_left_tile_pos[0]
        tile_h = self.map_widget.lower_right_tile_pos[1] - self.map_widget.upper_left_tile_pos[1]
        ul_x, ul_y = self.map_widget.upper_left_tile_pos
        zoom = round(self.map_widget.zoom)
        save_svg(
            active_layers=self.active_layers,
            file_path=file_path,
            width=width,
            height=height,
            scale=scale,
            ul_x=ul_x,
            ul_y=ul_y,
            tile_w=tile_w,
            tile_h=tile_h,
            zoom=zoom,
            transparent_background=self.basemap_menu.get() == "Transparent",
        )

    def _maximize_window(self):
        """Helper to maximize window state on Windows."""
        try:
            self.state('zoomed')
        except Exception:
            pass

if __name__ == "__main__":
    app = GTFSMapApp()
    app.mainloop()
