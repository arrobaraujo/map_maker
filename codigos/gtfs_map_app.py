import tkintermapview
import customtkinter as ctk
from tkinter import filedialog, messagebox, colorchooser
import sys
import os

print("--- DEBUG INFO ---")
print("GTFS Map Maker - Versão: 1.5.1 (PRO)")
from datetime import datetime
print(f"Executado em: {datetime.now()}")
print(f"TkinterMapView: {tkintermapview.__version__}")
print("------------------")
import time
from PIL import Image, ImageGrab, ImageDraw, ImageFont
import geopandas as gpd
from shapely.geometry import LineString

# High DPI awareness for Windows (fixes blurry text and "black" screenshots)
try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

# Add current directory to path so it can find gtfs_processor
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from gtfs_processor import GTFSProcessor
from tkintermapview import decimal_to_osm

class GTFSMapApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("GTFS Map Maker")
        self.geometry("1400x900")

        # Data state
        self.processor = None
        self.all_routes = []
        self.active_layers = {}  # {shape_id: {data}}
        self.selected_layer_id = None

        # UI Appearance
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        # Tile Cache Directory (Offline Database)
        self.tile_cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "map_tiles_cache")
        if not os.path.exists(self.tile_cache_dir):
            os.makedirs(self.tile_cache_dir)
        self.db_path = os.path.join(self.tile_cache_dir, "offline_tiles.db")

        self.setup_ui()

    def setup_ui(self):
        # Grid layout (1x2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left Sidebar
        self.sidebar = ctk.CTkFrame(self, width=340, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(3, weight=2) # Routes list
        self.sidebar.grid_rowconfigure(4, weight=1) # Active layers frame

        self.logo_label = ctk.CTkLabel(self.sidebar, text="GTFS Map Maker", font=ctk.CTkFont(size=22, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 10))

        self.load_button = ctk.CTkButton(self.sidebar, text="📁 Carregar GTFS (.zip)", 
                                        height=40, font=ctk.CTkFont(weight="bold"),
                                        command=self.load_gtfs)
        self.load_button.grid(row=1, column=0, padx=20, pady=20)

        self.search_entry = ctk.CTkEntry(self.sidebar, placeholder_text="🔍 Filtrar linhas...")
        self.search_entry.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.search_entry.bind("<KeyRelease>", self.filter_routes)

        self.route_listbox = ctk.CTkScrollableFrame(self.sidebar, label_text="Linhas Disponíveis")
        self.route_listbox.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")

        # Active Layers Section
        self.layer_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.layer_frame.grid(row=4, column=0, sticky="nsew", padx=20, pady=(10, 10))
        self.layer_frame.grid_rowconfigure(1, weight=1)
        self.layer_frame.grid_columnconfigure(0, weight=1)

        self.layer_label = ctk.CTkLabel(self.layer_frame, text="Camadas Ativas", font=ctk.CTkFont(size=14, weight="bold"))
        self.layer_label.grid(row=0, column=0, padx=0, pady=(0, 5), sticky="w")

        self.order_frame = ctk.CTkFrame(self.layer_frame, fg_color="transparent")
        self.order_frame.grid(row=0, column=1, pady=(0, 5), sticky="e")
        self.up_btn = ctk.CTkButton(self.order_frame, text="↑", width=30, height=24, command=lambda: self.move_layer(-1))
        self.up_btn.pack(side="left", padx=2)
        self.down_btn = ctk.CTkButton(self.order_frame, text="↓", width=30, height=24, command=lambda: self.move_layer(1))
        self.down_btn.pack(side="left", padx=2)

        self.layer_listbox = ctk.CTkScrollableFrame(self.layer_frame, label_text="Ordem: Cima > Baixo", height=200)
        self.layer_listbox.grid(row=1, column=0, sticky="nsew")

        # Right Main Area
        self.main_frame = ctk.CTkFrame(self, fg_color="#1a1a1a")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Style Controls (Top Bar)
        self.controls_frame = ctk.CTkFrame(self.main_frame, height=80, corner_radius=15, fg_color="#212121")
        self.controls_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(5, 15))
        
        self.color_btn = ctk.CTkButton(self.controls_frame, text="🎨 Cor", width=70, command=self.choose_color)
        self.color_btn.grid(row=0, column=0, padx=5, pady=15)

        self.width_label = ctk.CTkLabel(self.controls_frame, text="Espessura do shape: 3")
        self.width_label.grid(row=0, column=1, padx=(5, 0), pady=15)
        self.width_slider = ctk.CTkSlider(self.controls_frame, from_=1, to=15, number_of_steps=14, width=100, command=self.update_style)
        self.width_slider.set(3)
        self.width_slider.grid(row=0, column=2, padx=(2, 5), pady=15)

        self.fit_btn = ctk.CTkButton(self.controls_frame, text="📍 Focar Mapa", width=70, command=self.fit_map_buffer)
        self.fit_btn.grid(row=0, column=3, padx=5, pady=15)

        self.clear_btn = ctk.CTkButton(self.controls_frame, text="🗑️ Limpar", width=70, fg_color="#E74C3C", hover_color="#C0392B", command=self.clear_all_layers)
        self.clear_btn.grid(row=0, column=4, padx=5, pady=15)

        self.basemap_menu = ctk.CTkOptionMenu(self.controls_frame, values=["Carto Light", "Carto Dark", "Esri Light", "Esri Dark", "OpenStreetMap", "Google Normal", "Transparent"], width=130, command=self.change_basemap)
        self.basemap_menu.grid(row=0, column=5, padx=5, pady=15)

        self.dpi_label = ctk.CTkLabel(self.controls_frame, text="Qualidade (DPI):")
        self.dpi_label.grid(row=0, column=6, padx=(10, 2), pady=15)
        self.dpi_entry = ctk.CTkEntry(self.controls_frame, width=50)
        self.dpi_entry.insert(0, "150")
        self.dpi_entry.grid(row=0, column=7, padx=(2, 10), pady=15)

        self.save_btn = ctk.CTkButton(self.controls_frame, text="💾 Salvar", width=90, fg_color="#27AE60", hover_color="#219150", command=self.save_map)
        self.save_btn.grid(row=0, column=8, padx=10, pady=15)

        self.export_btn = ctk.CTkButton(self.controls_frame, text="🌐 Exportar SIG", width=110, fg_color="#8E44AD", hover_color="#9B59B6", command=self.export_sig)
        self.export_btn.grid(row=0, column=9, padx=10, pady=15)

        self.legend_switch = ctk.CTkCheckBox(self.controls_frame, text="Mostrar Legenda", command=self.toggle_legend_ui)
        self.legend_switch.select()
        self.legend_switch.grid(row=0, column=10, padx=10, pady=15)

        # Map View Area
        self.map_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.map_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.map_container.grid_rowconfigure(0, weight=1)
        self.map_container.grid_columnconfigure(0, weight=1)

        self.map_widget = tkintermapview.TkinterMapView(self.map_container, corner_radius=0, database_path=self.db_path) 
        self.map_widget.grid(row=0, column=0, sticky="nsew")
        self.map_widget.set_position(-22.9068, -43.1729) # Rio de Janeiro
        self.map_widget.set_zoom(12)
        
        # Legend (Floating Overlay)
        self.legend_frame = ctk.CTkFrame(self.map_widget, fg_color="white", bg_color="transparent", corner_radius=10, border_width=1, border_color="gray80")

        self.change_basemap("Carto Light")
        self.basemap_menu.set("Carto Light")
        self.update_legend()

    def load_gtfs(self):
        file_path = filedialog.askopenfilename(filetypes=[("GTFS ZIP", "*.zip")])
        if file_path:
            try:
                self.processor = GTFSProcessor(file_path)
                self.refresh_route_list()
                messagebox.showinfo("Sucesso", f"GTFS carregado!\n{len(self.all_routes)} rotas encontradas.")
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao carregar GTFS: {e}")

    def refresh_route_list(self):
        for widget in self.route_listbox.winfo_children():
            widget.destroy()
        if not self.processor: return
        self.all_routes = self.processor.get_route_list()
        self.display_routes(self.all_routes)

    def display_routes(self, routes):
        for route in routes:
            is_active = route['shape_id'] in self.active_layers
            btn = ctk.CTkButton(self.route_listbox, text=route['display_name'], 
                               fg_color="#34495E" if is_active else "transparent", 
                               hover_color="#2C3E50", anchor="w",
                               command=lambda r=route: self.toggle_route(r))
            btn.pack(fill="x", padx=5, pady=2)

    def filter_routes(self, event=None):
        if not self.processor: return
        query = self.search_entry.get().lower()
        filtered = [r for r in self.all_routes if query in r['display_name'].lower()]
        for widget in self.route_listbox.winfo_children():
            widget.destroy()
        self.display_routes(filtered)

    def toggle_route(self, route):
        shape_id = route['shape_id']
        if shape_id in self.active_layers:
            self.remove_layer(shape_id)
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
        if self.legend_switch.get():
            self.update_legend()

    def remove_layer(self, shape_id):
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
        for data in self.active_layers.values():
            if data.get('path_obj'):
                data['path_obj'].delete()
        self.active_layers = {}
        self.selected_layer_id = None
        self.refresh_layer_list()
        self.filter_routes()
        self.update_legend()

    def fit_map_buffer(self):
        if not self.active_layers: return
        all_coords = []
        for d in self.active_layers.values():
            all_coords.extend(d['coords'])
        if all_coords:
            lats = [c[0] for c in all_coords]
            lons = [c[1] for c in all_coords]
            self.map_widget.fit_bounding_box((max(lats), min(lons)), (min(lats), max(lons)))

    def refresh_layer_list(self):
        for widget in self.layer_listbox.winfo_children():
            widget.destroy()
        for shape_id, data in self.active_layers.items():
            is_sel = self.selected_layer_id == shape_id
            row = ctk.CTkFrame(self.layer_listbox, fg_color="transparent")
            row.pack(fill="x", padx=2, pady=2)
            btn = ctk.CTkButton(row, text=data['display_name'],
                               fg_color="#2980B9" if is_sel else "transparent",
                               command=lambda s=shape_id: self.select_layer(s))
            btn.pack(side="left", fill="x", expand=True, padx=(0, 2))
            del_btn = ctk.CTkButton(row, text="✕", width=30, height=32, command=lambda s=shape_id: self.remove_layer(s))
            del_btn.pack(side="right")

    def select_layer(self, shape_id):
        self.selected_layer_id = shape_id
        data = self.active_layers[shape_id]
        self.width_slider.set(data['width'])
        self.width_label.configure(text=f"Espessura do shape: {int(data['width'])}")
        self.refresh_layer_list()

    def choose_color(self):
        if not self.selected_layer_id: return
        color = colorchooser.askcolor(title="Escolha a cor da linha")[1]
        if color:
            self.active_layers[self.selected_layer_id]['color'] = color
            self.redraw_all_paths()
            self.update_legend()

    def update_style(self, value):
        if not self.selected_layer_id: return
        self.active_layers[self.selected_layer_id]['width'] = int(value)
        self.width_label.configure(text=f"Espessura do shape: {int(value)}")
        self.redraw_all_paths()

    def move_layer(self, direction):
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
        for data in self.active_layers.values():
            if data.get('path_obj'):
                data['path_obj'].delete()
        for shape_id, data in self.active_layers.items():
            data['path_obj'] = self.map_widget.set_path(data['coords'], color=data['color'], width=data['width'])

    def toggle_legend_ui(self):
        if self.legend_switch.get(): self.update_legend()
        else: self.legend_frame.place_forget()

    def update_legend(self):
        for widget in self.legend_frame.winfo_children(): widget.destroy()
        if not self.legend_switch.get():
            self.legend_frame.place_forget()
            return
        self.legend_frame.place(relx=0.02, rely=0.98, anchor="sw")
        self.legend_frame.lift()
        if not self.active_layers:
            ctk.CTkLabel(self.legend_frame, text="Selecione uma linha", font=ctk.CTkFont(size=14), text_color="black").pack(padx=15, pady=15)
            return
        
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
                    # Circular: Number - Long Name (Vista)
                    text = f"{sn} - {layer0.get('long_name', '')}".strip(" - ")
                elif len(sub_layers) > 1:
                    # Multiple directions: Number - Long Name
                    text = f"{sn} - {layer0.get('long_name', '')}".strip(" - ")
                else:
                    # Specific direction: display_name (Headsign + Direction)
                    text = layer0['display_name']
                
                row = ctk.CTkFrame(self.legend_frame, fg_color="transparent")
                row.pack(fill="x", padx=15, pady=5)
                ctk.CTkLabel(row, text=" ■ ", text_color=color, font=ctk.CTkFont(size=24)).pack(side="left")
                ctk.CTkLabel(row, text=text, font=ctk.CTkFont(size=13), text_color="black").pack(side="left", padx=5)

    def export_sig(self):
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
            messagebox.showinfo("Sucesso", "Exportado!")
        except Exception as e: messagebox.showerror("Erro", str(e))

    def change_basemap(self, choice):
        if choice == "OpenStreetMap":
            self.map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")
        elif choice == "Google Normal":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        elif choice in ["Esri Light", "Esri Dark"]:
            url = "World_Light_Gray_Base" if "Light" in choice else "World_Dark_Gray_Base"
            self.map_widget.set_tile_server(f"https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/{url}/MapServer/tile/{{z}}/{{y}}/{{x}}")
        elif choice in ["Carto Light", "Carto Dark"]:
            url = "light_all" if "Light" in choice else "dark_all"
            self.map_widget.set_tile_server(f"https://a.basemaps.cartocdn.com/{url}/{{z}}/{{x}}/{{y}}.png")
        elif choice == "Transparent":
            self.map_widget.set_tile_server("about:blank")
            self.map_widget.canvas.configure(bg="#00FF01")

    def save_map(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png"), ("PDF", "*.pdf")])
        if not file_path: return
        try:
            try: dpi = int(self.dpi_entry.get())
            except: dpi = 150
            scale = dpi / 96.0

            if self.basemap_menu.get() == "Transparent" and file_path.lower().endswith(".png"):
                # MODE A: Digital Rendering (No Fade, No Watermark, Manual Coords)
                w, h = self.map_container.winfo_width(), self.map_container.winfo_height()
                image = Image.new("RGBA", (int(w*scale), int(h*scale)), (255, 255, 255, 0))
                draw = ImageDraw.Draw(image)

                # Get tile dimensions for manual projection
                mw = self.map_widget
                tile_w = mw.lower_right_tile_pos[0] - mw.upper_left_tile_pos[0]
                tile_h = mw.lower_right_tile_pos[1] - mw.upper_left_tile_pos[1]
                ul_x, ul_y = mw.upper_left_tile_pos

                for data in self.active_layers.values():
                    points = []
                    for lat, lon in data['coords']:
                        # Manual Lat/Lon -> Pixel conversion
                        tx, ty = decimal_to_osm(lat, lon, round(mw.zoom))
                        px = ((tx - ul_x) / tile_w) * w
                        py = ((ty - ul_y) / tile_h) * h
                        points.append((px * scale, py * scale))
                    
                    if len(points) > 1:
                        draw.line(points, fill=data['color'], width=int(data['width'] * scale), joint="curve")
                
                if self.legend_switch.get() and self.active_layers:
                    lw, lh = 400*scale, (60 + len(self.active_layers)*30)*scale
                    lx, ly = 20*scale, (h*scale) - lh - 20*scale
                    draw.rectangle([lx, ly, lx+lw, ly+lh], fill="white", outline="gray")
                    try: font = ImageFont.truetype("arial.ttf", int(14*scale))
                    except: font = ImageFont.load_default()
                    curr_y = ly + 15*scale
                    for data in self.active_layers.values():
                        is_circular = "circular" in str(data.get('trip_headsign', '')).lower()
                        if is_circular:
                            legend_text = f"{data['short_name']} - {data.get('long_name', '')}".strip(" - ")
                        else:
                            legend_text = data['display_name']
                            
                        draw.rectangle([lx + 15*scale, curr_y, lx + 35*scale, curr_y + 20*scale], fill=data['color'])
                        draw.text((lx + 45*scale, curr_y), legend_text, fill="black", font=font)
                        curr_y += 30 * scale
            else:
                # MODE B: Screen Capture (Standard)
                self.map_widget.canvas.itemconfig("button", state='hidden')
                self.update(); time.sleep(0.5)
                x, y, w, h = self.map_container.winfo_rootx(), self.map_container.winfo_rooty(), self.map_container.winfo_width(), self.map_container.winfo_height()
                image = ImageGrab.grab(bbox=(x, y, x + w, y + h), all_screens=True)
                if scale > 1.1: image = image.resize((int(w*scale), int(h*scale)), Image.Resampling.LANCZOS)
                self.map_widget.canvas.itemconfig("button", state='normal')

            if file_path.endswith(".pdf"): image.convert("RGB").save(file_path, resolution=float(dpi))
            else: image.save(file_path, dpi=(dpi, dpi))
            messagebox.showinfo("Sucesso", "Salvo!")
        except Exception as e: messagebox.showerror("Erro", str(e))
        finally:
            if self.basemap_menu.get() != "Transparent":
                self.map_widget.canvas.itemconfig("button", state='normal')

if __name__ == "__main__":
    GTFSMapApp().mainloop()
