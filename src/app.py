import tkintermapview
import customtkinter as ctk
from tkinter import filedialog, messagebox, colorchooser
import sys
import os
import time
import logging
from datetime import datetime
from PIL import Image, ImageGrab
import geopandas as gpd
from shapely.geometry import LineString
from typing import List, Dict, Any, Optional

# Add the src/ directory to the path to ensure imports work correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from processor import GTFSProcessor
from utils.renderer import render_transparent_map

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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

        self.title("GTFS Map Maker")
        self.geometry("1400x900")
        
        # Open maximized on Windows (delayed to ensure it stays)
        self.after(0, lambda: self._maximize_window())

        # Application State
        self.processor: Optional[GTFSProcessor] = None
        self.all_routes: List[Dict] = []
        self.active_layers: Dict[str, Dict[str, Any]] = {}
        self.selected_layer_id: Optional[str] = None

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
        logger.info("Application initialized.")

    def setup_ui(self):
        """Sets up the graphical user interface components."""
        self.grid_columnconfigure(0, minsize=400)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar ---
        self.sidebar = ctk.CTkFrame(self, width=400, corner_radius=0)
        self.sidebar.grid_propagate(False) # Force width
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_columnconfigure(0, weight=1) # Ensure children fill width
        self.sidebar.grid_rowconfigure(3, weight=2)
        self.sidebar.grid_rowconfigure(4, weight=1)

        ctk.CTkLabel(self.sidebar, text="GTFS Map Maker", font=ctk.CTkFont(size=22, weight="bold")).grid(row=0, column=0, padx=20, pady=(30, 10))

        self.load_button = ctk.CTkButton(self.sidebar, text="📁 Carregar GTFS (.zip)", 
                                        height=40, font=ctk.CTkFont(weight="bold"), command=self.load_gtfs)
        self.load_button.grid(row=1, column=0, padx=20, pady=20)

        self.search_entry = ctk.CTkEntry(self.sidebar, placeholder_text="🔍 Filtrar linhas...")
        self.search_entry.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.search_entry.bind("<KeyRelease>", self.filter_routes)

        self.route_listbox = ctk.CTkScrollableFrame(self.sidebar, label_text="Linhas Disponíveis")
        self.route_listbox.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")

        # --- Active Layers Area ---
        self.layer_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.layer_frame.grid(row=4, column=0, sticky="nsew", padx=20, pady=(10, 10))
        self.layer_frame.grid_rowconfigure(1, weight=1)
        self.layer_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.layer_frame, text="Camadas Ativas", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, sticky="w")

        self.order_frame = ctk.CTkFrame(self.layer_frame, fg_color="transparent")
        self.order_frame.grid(row=0, column=1, sticky="e")
        ctk.CTkButton(self.order_frame, text="↑", width=30, height=24, command=lambda: self.move_layer(-1)).pack(side="left", padx=2)
        ctk.CTkButton(self.order_frame, text="↓", width=30, height=24, command=lambda: self.move_layer(1)).pack(side="left", padx=2)

        self.layer_listbox = ctk.CTkScrollableFrame(self.layer_frame, label_text="Ordem: Cima > Baixo", height=200)
        self.layer_listbox.grid(row=1, column=0, columnspan=2, sticky="nsew")

        # --- Main Area ---
        self.main_frame = ctk.CTkFrame(self, fg_color="#1a1a1a")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Controls
        self.controls_frame = ctk.CTkFrame(self.main_frame, height=80, corner_radius=15, fg_color="#212121")
        self.controls_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(5, 15))
        
        ctk.CTkButton(self.controls_frame, text="🎨 Cor", width=70, command=self.choose_color).grid(row=0, column=0, padx=5, pady=15)
        self.width_label = ctk.CTkLabel(self.controls_frame, text="Espessura: 3")
        self.width_label.grid(row=0, column=1, padx=(5, 0), pady=15)
        self.width_slider = ctk.CTkSlider(self.controls_frame, from_=1, to=15, number_of_steps=14, width=80, command=self.update_style)
        self.width_slider.set(3)
        self.width_slider.grid(row=0, column=2, padx=(2, 5), pady=15)

        ctk.CTkButton(self.controls_frame, text="📍 Focar", width=70, command=self.fit_map_buffer).grid(row=0, column=3, padx=5, pady=15)

        # Zoom Controls (Buttons + Entry)
        self.zoom_minus_btn = ctk.CTkButton(self.controls_frame, text="-", width=30, command=lambda: self.adjust_zoom(-1.0))
        self.zoom_minus_btn.grid(row=0, column=4, padx=(5, 2), pady=15)
        
        self.zoom_entry = ctk.CTkEntry(self.controls_frame, width=50)
        self.zoom_entry.insert(0, "12")
        self.zoom_entry.grid(row=0, column=5, padx=2, pady=15)
        self.zoom_entry.bind("<Return>", lambda e: self.update_zoom_from_entry())
        
        self.zoom_plus_btn = ctk.CTkButton(self.controls_frame, text="+", width=30, command=lambda: self.adjust_zoom(1.0))
        self.zoom_plus_btn.grid(row=0, column=6, padx=(2, 5), pady=15)

        self.basemap_menu = ctk.CTkOptionMenu(self.controls_frame, values=["Carto Light", "Carto Dark", "Esri Light", "Esri Dark", "OpenStreetMap", "Google Normal", "Transparent"], width=130, command=self.change_basemap)
        self.basemap_menu.grid(row=0, column=7, padx=5, pady=15)
        self.basemap_menu.set("Carto Light")

        ctk.CTkLabel(self.controls_frame, text="DPI:").grid(row=0, column=8, padx=(10, 2), pady=15)
        self.dpi_entry = ctk.CTkEntry(self.controls_frame, width=50)
        self.dpi_entry.insert(0, "300")
        self.dpi_entry.grid(row=0, column=9, padx=(2, 10), pady=15)

        ctk.CTkButton(self.controls_frame, text="💾 Salvar", width=90, fg_color="#27AE60", hover_color="#219150", command=self.save_map).grid(row=0, column=10, padx=10, pady=15)
        ctk.CTkButton(self.controls_frame, text="🌐 Exportar SIG", width=110, fg_color="#8E44AD", hover_color="#9B59B6", command=self.export_sig).grid(row=0, column=11, padx=10, pady=15)

        self.legend_switch = ctk.CTkCheckBox(self.controls_frame, text="Legenda", command=self.toggle_legend_ui)
        self.legend_switch.select()
        self.legend_switch.grid(row=0, column=12, padx=10, pady=15)

        ctk.CTkButton(self.controls_frame, text="🗑️ Limpar", width=70, fg_color="#E74C3C", hover_color="#C0392B", command=self.clear_all_layers).grid(row=0, column=13, padx=10, pady=15)

        # Map View
        self.map_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.map_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.map_container.grid_rowconfigure(0, weight=1)
        self.map_container.grid_columnconfigure(0, weight=1)

        self.map_widget = tkintermapview.TkinterMapView(self.map_container, corner_radius=0, database_path=self.db_path)
        self.map_widget.grid(row=0, column=0, sticky="nsew")
        self.map_widget.set_position(-22.9068, -43.1729)
        self.map_widget.set_zoom(12)
        
        # Sync Slider on Mouse Wheel
        self.map_widget.canvas.bind("<MouseWheel>", lambda e: self.after(100, self.sync_zoom_from_map), add="+")

        # Overlay Legend
        self.legend_frame = ctk.CTkFrame(self.map_widget, fg_color="white", bg_color="transparent", corner_radius=10, border_width=1, border_color="gray80")

        self.change_basemap("Carto Light")
        self.update_legend()

    def load_gtfs(self):
        """Opens a file dialog to load a GTFS ZIP file."""
        file_path = filedialog.askopenfilename(filetypes=[("GTFS ZIP", "*.zip")])
        if file_path:
            try:
                self.processor = GTFSProcessor(file_path)
                self.refresh_route_list()
                messagebox.showinfo("Sucesso", f"GTFS carregado!\n{len(self.all_routes)} rotas encontradas.")
            except Exception as e:
                logger.exception("Failed to load GTFS")
                messagebox.showerror("Erro", f"Falha ao carregar GTFS: {e}")

    def refresh_route_list(self):
        """Refreshes the sidebar list of available routes."""
        for widget in self.route_listbox.winfo_children():
            widget.destroy()
        if not self.processor: return
        self.all_routes = self.processor.get_route_list()
        self._display_routes(self.all_routes)

    def _display_routes(self, routes: List[Dict]):
        """Internal helper to render buttons for each route."""
        for route in routes:
            is_active = route['shape_id'] in self.active_layers
            btn = ctk.CTkButton(self.route_listbox, text=route['display_name'], 
                               fg_color="#34495E" if is_active else "transparent", 
                               hover_color="#2C3E50", anchor="w",
                               command=lambda r=route: self.toggle_route(r))
            btn.pack(fill="x", padx=5, pady=2, expand=True)

    def filter_routes(self, event=None):
        """Filters the route list based on the search entry text."""
        if not self.processor: return
        query = self.search_entry.get().lower()
        filtered = [r for r in self.all_routes if query in r['display_name'].lower()]
        for widget in self.route_listbox.winfo_children(): widget.destroy()
        self._display_routes(filtered)

    def toggle_route(self, route: Dict):
        """Add or removes a route from the map."""
        shape_id = route['shape_id']
        if shape_id in self.active_layers:
            self._remove_layer(shape_id)
        else:
            coords = self.processor.get_shape_coordinates(shape_id)
            if not coords:
                messagebox.showwarning("Aviso", f"Sem coordenadas para {shape_id}")
                return
            
            colors = ["#1ABC9C", "#E74C3C", "#3498DB", "#F1C40F", "#9B59B6", "#E67E22", "#2ECC71"]
            color = colors[len(self.active_layers) % len(colors)]
            path_obj = self.map_widget.set_path(coords, color=color, width=3)
            
            self.active_layers[shape_id] = {
                'shape_id': shape_id,
                'display_name': route['display_name'],
                'short_name': route.get('short_name', ''),
                'long_name': route.get('long_name', ''),
                'direction': route.get('direction', ''),
                'trip_headsign': route.get('trip_headsign', ''),
                'path_obj': path_obj,
                'color': color,
                'width': 3,
                'coords': coords
            }
            self.selected_layer_id = shape_id
        
        self.refresh_layer_list()
        self.filter_routes()
        self.redraw_all_paths()
        self.update_legend()

    def _remove_layer(self, shape_id: str):
        """Internal helper to remove a specific layer."""
        if shape_id in self.active_layers:
            if self.active_layers[shape_id].get('path_obj'):
                self.active_layers[shape_id]['path_obj'].delete()
            self.active_layers.pop(shape_id, None)
            if self.selected_layer_id == shape_id:
                self.selected_layer_id = None
            self.refresh_layer_list()
            self.filter_routes()
            self.redraw_all_paths()
            self.update_legend()

    def clear_all_layers(self):
        """Removes all layers from the map."""
        for data in self.active_layers.values():
            if data.get('path_obj'): data['path_obj'].delete()
        self.active_layers = {}
        self.selected_layer_id = None
        self.refresh_layer_list()
        self.filter_routes()
        self.update_legend()

    def fit_map_buffer(self):
        """Adjusts the map zoom and position to fit all active layers."""
        if not self.active_layers: return
        all_coords = []
        for d in self.active_layers.values(): all_coords.extend(d['coords'])
        if all_coords:
            lats = [c[0] for c in all_coords]
            lons = [c[1] for c in all_coords]
            self.map_widget.fit_bounding_box((max(lats), min(lons)), (min(lats), max(lons)))
            # Sync slider after fit
            self.after(500, self.sync_zoom_from_map)

    def adjust_zoom(self, delta):
        """Increments or decrements the zoom by delta."""
        current_zoom = round(float(self.map_widget.zoom))
        new_zoom = int(max(1, min(19, current_zoom + delta)))
        self.map_widget.set_zoom(new_zoom)
        self.after(200, self.sync_zoom_from_map)

    def update_zoom_from_entry(self):
        """Updates the map zoom based on the entry field value."""
        try:
            val = float(self.zoom_entry.get().replace(',', '.'))
            new_zoom = int(round(max(1, min(19, val))))
            self.map_widget.set_zoom(new_zoom)
            self.after(200, self.sync_zoom_from_map)
        except ValueError:
            self.sync_zoom_from_map()

    def sync_zoom_from_map(self):
        """Synchronizes the entry field with the current map zoom level."""
        current_zoom = int(round(float(self.map_widget.zoom)))
        self.zoom_entry.delete(0, "end")
        self.zoom_entry.insert(0, str(current_zoom))
    def refresh_layer_list(self):
        """Updates the active layers list in the sidebar."""
        for widget in self.layer_listbox.winfo_children(): widget.destroy()
        for shape_id, data in self.active_layers.items():
            is_sel = self.selected_layer_id == shape_id
            row = ctk.CTkFrame(self.layer_listbox, fg_color="transparent")
            row.pack(fill="x", padx=2, pady=2)
            btn = ctk.CTkButton(row, text=data['display_name'],
                               fg_color="#2980B9" if is_sel else "transparent",
                               command=lambda s=shape_id: self.select_layer(s))
            btn.pack(side="left", fill="x", expand=True, padx=(0, 2))
            ctk.CTkButton(row, text="✕", width=30, height=32, command=lambda s=shape_id: self._remove_layer(s)).pack(side="right")

    def select_layer(self, shape_id: str):
        """Sets a layer as the currently selected one for styling."""
        self.selected_layer_id = shape_id
        data = self.active_layers[shape_id]
        self.width_slider.set(data['width'])
        self.width_label.configure(text=f"Espessura: {int(data['width'])}")
        self.refresh_layer_list()

    def choose_color(self):
        """Opens a color chooser for the selected layer."""
        if not self.selected_layer_id: return
        color = colorchooser.askcolor(title="Escolha a cor da linha")[1]
        if color:
            self.active_layers[self.selected_layer_id]['color'] = color
            self.redraw_all_paths()
            self.update_legend()

    def update_style(self, value):
        """Updates the line width for the selected layer."""
        if not self.selected_layer_id: return
        self.active_layers[self.selected_layer_id]['width'] = int(value)
        self.width_label.configure(text=f"Espessura: {int(value)}")
        self.redraw_all_paths()

    def move_layer(self, direction: int):
        """Changes the rendering order of layers."""
        if not self.selected_layer_id: return
        keys = list(self.active_layers.keys())
        idx = keys.index(self.selected_layer_id)
        new_idx = idx + direction
        if 0 <= new_idx < len(keys):
            keys[idx], keys[new_idx] = keys[new_idx], keys[idx]
            self.active_layers = {k: self.active_layers[k] for k in keys}
            self.redraw_all_paths()
            self.refresh_layer_list()
            self.update_legend()

    def redraw_all_paths(self):
        """Redraws all paths on the map widgets according to their order and style."""
        for data in self.active_layers.values():
            if data.get('path_obj'): data['path_obj'].delete()
        for shape_id, data in self.active_layers.items():
            data['path_obj'] = self.map_widget.set_path(data['coords'], color=data['color'], width=data['width'])

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
        
        # Grouping logic to match original behavior
        groups = {}
        for data in self.active_layers.values():
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
                    text = f"{sn} - {layer0.get('long_name', '')}".strip(" - ")
                elif len(sub_layers) > 1:
                    text = f"{sn} - {layer0.get('long_name', '')}".strip(" - ")
                else:
                    text = layer0['display_name']
                
                row = ctk.CTkFrame(self.legend_frame, fg_color="transparent")
                row.pack(fill="x", padx=15, pady=5)
                ctk.CTkLabel(row, text=" ■ ", text_color=color, font=ctk.CTkFont(size=24)).pack(side="left")
                ctk.CTkLabel(row, text=text, font=ctk.CTkFont(size=13), text_color="black").pack(side="left", padx=5)

    def export_sig(self):
        """Exports active layers as GeoPackage or Shapefile."""
        if not self.active_layers: return
        file_path = filedialog.asksaveasfilename(defaultextension=".gpkg", filetypes=[("GeoPackage", "*.gpkg"), ("Shapefile", "*.shp")])
        if not file_path: return
        try:
            features = []
            for shape_id, data in self.active_layers.items():
                coords_lonlat = [(c[1], c[0]) for c in data['coords']]
                features.append({'geometry': LineString(coords_lonlat), 'shape_id': shape_id, 'name': data['display_name'], 'color': data['color']})
            gdf = gpd.GeoDataFrame(features, crs="EPSG:4326")
            gdf.to_file(file_path, driver="ESRI Shapefile" if file_path.endswith(".shp") else "GPKG")
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
        """Saves the current map as an image (PNG/PDF)."""
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png"), ("PDF", "*.pdf")])
        if not file_path: return
        try:
            try: dpi = int(self.dpi_entry.get())
            except: dpi = 150
            scale = dpi / 96.0

            if self.basemap_menu.get() == "Transparent" and file_path.lower().endswith(".png"):
                # Use decoupled rendering logic for high-quality transparent export
                image = render_transparent_map(
                    self.map_container.winfo_width(),
                    self.map_container.winfo_height(),
                    scale,
                    self.active_layers,
                    self.map_widget,
                    self.legend_switch.get()
                )
            else:
                # Standard screen capture
                self.map_widget.canvas.itemconfig("button", state='hidden')
                self.update()
                time.sleep(0.5)
                x, y, w, h = self.map_container.winfo_rootx(), self.map_container.winfo_rooty(), self.map_container.winfo_width(), self.map_container.winfo_height()
                image = ImageGrab.grab(bbox=(x, y, x + w, y + h), all_screens=True)
                if scale > 1.1: image = image.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
                self.map_widget.canvas.itemconfig("button", state='normal')

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

    def _maximize_window(self):
        """Helper to maximize window state on Windows."""
        try:
            self.state('zoomed')
        except Exception:
            pass

if __name__ == "__main__":
    app = GTFSMapApp()
    app.mainloop()
