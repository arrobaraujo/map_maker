import customtkinter as ctk
import tkintermapview
from tkinter import filedialog, messagebox, colorchooser
import sys
import os
import time
from PIL import Image, ImageGrab

# High DPI awareness for Windows (fixes blurry text and "black" screenshots)
try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

# Add current directory to path so it can find gtfs_processor
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from gtfs_processor import GTFSProcessor

class GTFSMapApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("GTFS Map Explorer - R_SMTR")
        self.geometry("1400x900")

        # Data state
        self.processor = None
        self.all_routes = []
        self.active_layers = {}  # {shape_id: {data}}
        self.selected_layer_id = None

        # UI Appearance
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.setup_ui()

    def setup_ui(self):
        # Grid layout (1x2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left Sidebar
        self.sidebar = ctk.CTkFrame(self, width=320, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar, text="GTFS Map Explorer", font=ctk.CTkFont(size=22, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 10))

        self.load_button = ctk.CTkButton(self.sidebar, text="📁 Carregar GTFS (.zip)", 
                                        height=40, font=ctk.CTkFont(weight="bold"),
                                        command=self.load_gtfs)
        self.load_button.grid(row=1, column=0, padx=20, pady=20)

        self.search_entry = ctk.CTkEntry(self.sidebar, placeholder_text="🔍 Filtrar rotas...")
        self.search_entry.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.search_entry.bind("<KeyRelease>", self.filter_routes)

        self.route_listbox = ctk.CTkScrollableFrame(self.sidebar, label_text="Rotas Disponíveis")
        self.route_listbox.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")

        # Active Layers Section
        self.layer_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.layer_frame.grid(row=4, column=0, sticky="nsew", padx=20, pady=(10, 10))
        self.layer_frame.grid_rowconfigure(1, weight=1)
        self.layer_frame.grid_columnconfigure(0, weight=1)

        self.layer_label = ctk.CTkLabel(self.layer_frame, text="Camadas Ativas", font=ctk.CTkFont(size=14, weight="bold"))
        self.layer_label.grid(row=0, column=0, padx=0, pady=(0, 5), sticky="w")

        self.layer_listbox = ctk.CTkScrollableFrame(self.layer_frame, label_text="Ordem: Cima -> Baixo", height=200)
        self.layer_listbox.grid(row=1, column=0, sticky="nsew")

        # Right Main Area
        self.main_frame = ctk.CTkFrame(self, fg_color="#1a1a1a") # Solid color for dark mode
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Style Controls (Top Bar)
        self.controls_frame = ctk.CTkFrame(self.main_frame, height=80, corner_radius=15, fg_color="#212121")
        self.controls_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(5, 15))
        
        self.color_btn = ctk.CTkButton(self.controls_frame, text="🎨 Cor", width=70, command=self.choose_color)
        self.color_btn.grid(row=0, column=0, padx=5, pady=15)

        self.width_label = ctk.CTkLabel(self.controls_frame, text="Espessura: 3")
        self.width_label.grid(row=0, column=1, padx=(5, 0), pady=15)
        self.width_slider = ctk.CTkSlider(self.controls_frame, from_=1, to=15, number_of_steps=14, width=100, command=self.update_style)
        self.width_slider.set(3)
        self.width_slider.grid(row=0, column=2, padx=(2, 5), pady=15)

        self.order_frame = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        self.order_frame.grid(row=0, column=3, padx=5)
        self.up_btn = ctk.CTkButton(self.order_frame, text="↑", width=35, command=lambda: self.move_layer(-1))
        self.up_btn.pack(side="left", padx=2)
        self.down_btn = ctk.CTkButton(self.order_frame, text="↓", width=35, command=lambda: self.move_layer(1))
        self.down_btn.pack(side="left", padx=2)

        self.fit_btn = ctk.CTkButton(self.controls_frame, text="📍 Focar", width=70, command=self.fit_map_buffer)
        self.fit_btn.grid(row=0, column=4, padx=5, pady=15)

        self.clear_btn = ctk.CTkButton(self.controls_frame, text="🗑️ Limpar", width=70, fg_color="#E74C3C", hover_color="#C0392B", command=self.clear_all_layers)
        self.clear_btn.grid(row=0, column=5, padx=5, pady=15)

        self.basemap_menu = ctk.CTkOptionMenu(self.controls_frame, values=["Esri Light", "Esri Dark", "Carto Light", "Carto Dark", "OpenStreetMap", "Google Normal"], width=130, command=self.change_basemap)
        self.basemap_menu.grid(row=0, column=6, padx=5, pady=15)

        self.save_btn = ctk.CTkButton(self.controls_frame, text="💾 Salvar", width=90, fg_color="#27AE60", hover_color="#219150", command=self.save_map)
        self.save_btn.grid(row=0, column=7, padx=10, pady=15)

        # Map View Area (contains map + legend overlay)
        self.map_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.map_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.map_container.grid_rowconfigure(0, weight=1)
        self.map_container.grid_columnconfigure(0, weight=1)

        self.map_widget = tkintermapview.TkinterMapView(self.map_container, corner_radius=0) 
        self.map_widget.grid(row=0, column=0, sticky="nsew")
        self.map_widget.set_position(-22.9068, -43.1729) # Rio de Janeiro
        self.map_widget.set_zoom(12)
        
        # Legend (Floating Overlay)
        self.legend_frame = ctk.CTkFrame(self.map_container, fg_color=("#F0F0F0", "#212121"), corner_radius=10, border_width=2, border_color="gray30")
        self.legend_frame_visible = False # Shared state

        self.change_basemap("Esri Light") 

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
            if 'path_obj' in self.active_layers[shape_id] and self.active_layers[shape_id]['path_obj']:
                self.active_layers[shape_id]['path_obj'].delete()
            self.active_layers.pop(shape_id, None)
            if self.selected_layer_id == shape_id:
                self.selected_layer_id = None
        else:
            coords = self.processor.get_shape_coordinates(shape_id)
            if not coords:
                messagebox.showwarning("Aviso", f"Sem coordenadas para {shape_id}")
                return
            
            colors = ["#1ABC9C", "#E74C3C", "#3498DB", "#F1C40F", "#9B59B6", "#E67E22", "#2ECC71"]
            color = colors[len(self.active_layers) % len(colors)]
            path_obj = self.map_widget.set_path(coords, color=color, width=3)
            
            self.active_layers[shape_id] = {
                'display_name': route['display_name'],
                'short_name': route.get('short_name', ''),
                'direction': route.get('direction', ''),
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

    def clear_all_layers(self):
        for data in self.active_layers.values():
            if 'path_obj' in data and data['path_obj']:
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
            btn = ctk.CTkButton(self.layer_listbox, text=data['display_name'],
                               fg_color="#2980B9" if is_sel else "transparent",
                               command=lambda s=shape_id: self.select_layer(s))
            btn.pack(fill="x", padx=5, pady=2)

    def select_layer(self, shape_id):
        self.selected_layer_id = shape_id
        data = self.active_layers[shape_id]
        self.width_slider.set(data['width'])
        self.width_label.configure(text=f"Espessura: {int(data['width'])}")
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
        self.width_label.configure(text=f"Espessura: {int(value)}")
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
            if 'path_obj' in data and data['path_obj']:
                data['path_obj'].delete()
        for shape_id, data in self.active_layers.items():
            data['path_obj'] = self.map_widget.set_path(data['coords'], color=data['color'], width=data['width'])

    def update_legend(self):
        # Clear previous legend
        for widget in self.legend_frame.winfo_children():
            widget.destroy()
        
        if not self.active_layers:
            self.legend_frame.place_forget()
            return

        self.legend_frame.place(relx=0.98, rely=0.98, anchor="se", padx=10, pady=10)
        
        title = ctk.CTkLabel(self.legend_frame, text="Legenda", font=ctk.CTkFont(size=12, weight="bold"))
        title.pack(padx=10, pady=(5, 2))
        
        # Add entry for each active layer (in z-order, assuming last added/top of list is top of legend?)
        # Actually user might want top drawn at top of legend. 
        # Our move_layer moves them in the dict. Let's show in drawing order.
        for data in reversed(list(self.active_layers.values())):
            row = ctk.CTkFrame(self.legend_frame, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=2)
            
            # Color indicator
            color_box = ctk.CTkLabel(row, text=" ■ ", text_color=data['color'], font=ctk.CTkFont(size=20))
            color_box.pack(side="left")
            
            # Text
            txt = f"{data['display_name']}"
            lbl = ctk.CTkLabel(row, text=txt, font=ctk.CTkFont(size=11))
            lbl.pack(side="left", padx=5)

    def change_basemap(self, choice):
        if choice == "OpenStreetMap":
            self.map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")
        elif choice == "Google Normal":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        elif choice == "Esri Light":
            self.map_widget.set_tile_server("https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}")
        elif choice == "Esri Dark":
            self.map_widget.set_tile_server("https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}")
        elif choice == "Carto Light":
            self.map_widget.set_tile_server("https://a.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png")
        elif choice == "Carto Dark":
            self.map_widget.set_tile_server("https://a.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png")

    def save_map(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png", 
                                                 filetypes=[("PNG Image", "*.png"), ("PDF Document", "*.pdf")])
        if not file_path: return

        try:
            # Important: Give some time for UI to update and ensure it's not obscured
            self.update()
            time.sleep(0.5)
            
            # Get widget root coordinates
            # Note: winfo_rootx includes DPI scaling on Windows if SetProcessDpiAwareness(1) is set
            x = self.map_container.winfo_rootx()
            y = self.map_container.winfo_rooty()
            w = self.map_container.winfo_width()
            h = self.map_container.winfo_height()
            
            # Use bbox to grab the container which includes map + legend
            # We capture the screen area
            image = ImageGrab.grab(bbox=(x, y, x + w, y + h), all_screens=True)
            
            if file_path.endswith(".pdf"):
                image.convert("RGB").save(file_path, "PDF", resolution=100.0)
            else:
                image.save(file_path)
            
            messagebox.showinfo("Sucesso", f"Mapa salvo em: {file_path}")
        except Exception as e:
            messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar o mapa: {e}\nAtente-se que o Pillow deve estar instalado.")

if __name__ == "__main__":
    app = GTFSMapApp()
    app.mainloop()
