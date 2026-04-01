import customtkinter as ctk
import tkintermapview


def build_main_ui(app):
    """Builds and wires all UI widgets into the app instance."""
    app.grid_columnconfigure(0, minsize=400)
    app.grid_columnconfigure(1, weight=1)
    app.grid_rowconfigure(0, weight=1)

    # --- Sidebar ---
    app.sidebar = ctk.CTkFrame(app, width=400, corner_radius=0)
    app.sidebar.grid_propagate(False)
    app.sidebar.grid(row=0, column=0, sticky="nsew")
    app.sidebar.grid_columnconfigure(0, weight=1)
    app.sidebar.grid_rowconfigure(3, weight=2)
    app.sidebar.grid_rowconfigure(4, weight=1)

    ctk.CTkLabel(app.sidebar, text="GTFS Map Maker", font=ctk.CTkFont(size=22, weight="bold")).grid(
        row=0, column=0, padx=20, pady=(30, 10)
    )

    app.load_button = ctk.CTkButton(
        app.sidebar,
        text="📁 Carregar GTFS (.zip)",
        height=40,
        font=ctk.CTkFont(weight="bold"),
        command=app.load_gtfs,
    )
    app.load_button.grid(row=1, column=0, padx=20, pady=20)

    app.search_entry = ctk.CTkEntry(app.sidebar, placeholder_text="🔍 Filtrar linhas...")
    app.search_entry.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
    app.search_entry.bind("<KeyRelease>", app.filter_routes)

    app.route_listbox = ctk.CTkFrame(app.sidebar)
    app.route_listbox.grid(row=3, column=0, padx=20, pady=(10, 0), sticky="nsew")

    ctk.CTkLabel(app.route_listbox, text="Linhas Disponíveis", font=ctk.CTkFont(size=13, weight="bold")).pack(
        pady=(5, 0)
    )

    # --- Active Layers Area ---
    app.layer_frame = ctk.CTkFrame(app.sidebar, fg_color="transparent")
    app.layer_frame.grid(row=4, column=0, sticky="nsew", padx=20, pady=(10, 10))
    app.layer_frame.grid_rowconfigure(1, weight=1)
    app.layer_frame.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(app.layer_frame, text="Camadas Ativas", font=ctk.CTkFont(size=14, weight="bold")).grid(
        row=0, column=0, sticky="w"
    )

    app.order_frame = ctk.CTkFrame(app.layer_frame, fg_color="transparent")
    app.order_frame.grid(row=0, column=1, sticky="e")
    ctk.CTkButton(app.order_frame, text="↑", width=30, height=24, command=lambda: app.move_layer(-1)).pack(
        side="left", padx=2
    )
    ctk.CTkButton(app.order_frame, text="↓", width=30, height=24, command=lambda: app.move_layer(1)).pack(
        side="left", padx=2
    )

    app.layer_listbox = ctk.CTkScrollableFrame(app.layer_frame, label_text="Ordem: Cima > Baixo", height=200)
    app.layer_listbox.grid(row=1, column=0, columnspan=2, sticky="nsew")

    # --- Main Area ---
    app.main_frame = ctk.CTkFrame(app, fg_color="#1a1a1a")
    app.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
    app.main_frame.grid_rowconfigure(1, weight=1)
    app.main_frame.grid_columnconfigure(0, weight=1)

    app.controls_frame = ctk.CTkFrame(app.main_frame, height=80, corner_radius=15, fg_color="#212121")
    app.controls_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(5, 15))

    ctk.CTkButton(app.controls_frame, text="🎨 Cor", width=70, command=app.choose_color).grid(row=0, column=0, padx=5, pady=15)
    app.width_label = ctk.CTkLabel(app.controls_frame, text="Espessura: 3")
    app.width_label.grid(row=0, column=1, padx=(5, 0), pady=15)
    app.width_slider = ctk.CTkSlider(
        app.controls_frame,
        from_=1,
        to=15,
        number_of_steps=14,
        width=80,
        command=app.update_style,
    )
    app.width_slider.set(3)
    app.width_slider.grid(row=0, column=2, padx=(2, 5), pady=15)

    ctk.CTkButton(app.controls_frame, text="📍 Focar", width=70, command=app.fit_map_buffer).grid(row=0, column=3, padx=5, pady=15)

    app.zoom_minus_btn = ctk.CTkButton(app.controls_frame, text="-", width=30, command=lambda: app.adjust_zoom(-0.1))
    app.zoom_minus_btn.grid(row=0, column=4, padx=(5, 2), pady=15)

    app.zoom_entry = ctk.CTkEntry(app.controls_frame, width=50)
    app.zoom_entry.insert(0, "12.0")
    app.zoom_entry.grid(row=0, column=5, padx=2, pady=15)
    app.zoom_entry.bind("<Return>", lambda e: app.update_zoom_from_entry())

    app.zoom_plus_btn = ctk.CTkButton(app.controls_frame, text="+", width=30, command=lambda: app.adjust_zoom(0.1))
    app.zoom_plus_btn.grid(row=0, column=6, padx=(2, 5), pady=15)

    app.basemap_menu = ctk.CTkOptionMenu(
        app.controls_frame,
        values=[
            "Carto Light",
            "Carto Dark",
            "Esri Light",
            "Esri Dark",
            "OpenStreetMap",
            "Google Normal",
            "Transparent",
        ],
        width=130,
        command=app.change_basemap,
    )
    app.basemap_menu.grid(row=0, column=7, padx=5, pady=15)
    app.basemap_menu.set("Carto Light")

    ctk.CTkLabel(app.controls_frame, text="DPI:").grid(row=0, column=8, padx=(10, 2), pady=15)
    app.dpi_entry = ctk.CTkEntry(app.controls_frame, width=50)
    app.dpi_entry.insert(0, "300")
    app.dpi_entry.grid(row=0, column=9, padx=(2, 10), pady=15)

    ctk.CTkButton(app.controls_frame, text="💾 Salvar", width=90, fg_color="#27AE60", hover_color="#219150", command=app.save_map).grid(
        row=0, column=10, padx=10, pady=15
    )
    ctk.CTkButton(
        app.controls_frame,
        text="🌐 Exportar SIG",
        width=110,
        fg_color="#8E44AD",
        hover_color="#9B59B6",
        command=app.export_sig,
    ).grid(row=0, column=11, padx=10, pady=15)

    app.legend_switch = ctk.CTkCheckBox(app.controls_frame, text="Legenda", command=app.toggle_legend_ui)
    app.legend_switch.select()
    app.legend_switch.grid(row=0, column=12, padx=10, pady=15)

    ctk.CTkButton(
        app.controls_frame,
        text="🗑️ Limpar",
        width=70,
        fg_color="#E74C3C",
        hover_color="#C0392B",
        command=app.clear_all_layers,
    ).grid(row=0, column=13, padx=10, pady=15)

    # Map View
    app.map_container = ctk.CTkFrame(app.main_frame, fg_color="transparent")
    app.map_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
    app.map_container.grid_rowconfigure(0, weight=1)
    app.map_container.grid_columnconfigure(0, weight=1)

    app.map_widget = tkintermapview.TkinterMapView(app.map_container, corner_radius=0, database_path=app.db_path)
    app.map_widget.grid(row=0, column=0, sticky="nsew")

    try:
        app.map_widget.set_tile_cache_max_size(2000)
    except AttributeError:
        pass

    app.map_widget.set_position(-22.9068, -43.1729)
    app.map_widget.set_zoom(12)
    app.map_widget.canvas.bind("<MouseWheel>", lambda e: app.after(100, app.sync_zoom_from_map), add="+")

    # Overlay Legend
    app.legend_frame = ctk.CTkFrame(
        app.map_widget,
        fg_color="white",
        bg_color="transparent",
        corner_radius=10,
        border_width=1,
        border_color="gray80",
    )

    app.change_basemap("Carto Light")
    app.update_legend()
