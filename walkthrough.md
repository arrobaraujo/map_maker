# Walkthrough - GTFS Map GUI

This application allows you to visualize and customize GTFS route itinerários using a modern graphical interface.

## Prerequisites
Ensure you have the required libraries installed:
```bash
pip install customtkinter tkintermapview pandas geopandas shapely pyogrio
```

## How to Use

### 1. Launching the App
Run the main script:
```bash
python gtfs_map_app.py
```

### 2. Loading GTFS Data
Click the **"Carregar GTFS (.zip)"** button and select your GTFS file. The app will parse `routes.txt`, `trips.txt`, and `shapes.txt`.

### 3. Selecting Routes
- Use the **Search Bar** to filter specific lines by name.
- Click a route in the **"Rotas Disponíveis"** list to add it to the map.
- Active routes are highlighted in the list.

### 4. Customizing Styles
- Select an active layer from the **"Camadas Ativas"** list.
- Click **"Cor"** to open a color picker.
- Use the **"Espessura"** slider to adjust the line width.

### 5. Managing Layers
- Use the **↑** and **↓** buttons to move the selected layer up or down. Layers at the top of the list will be drawn last (on top of others).
- Click **"Focar"** to zoom and center the map on all active routes.
- Click **"Limpar"** to remove all layers.

### 6. Saving the Map
- Click the **"Salvar"** button in the top bar.
- Choose between **PNG** or **PDF** format and select the destination.
- *Note: Requires `Pillow` installed.*

### 7. Changing Basemaps
- Choose between **Esri Light/Dark**, **Carto Light/Dark**, **OpenStreetMap**, or **Google** options from the dropdown menu.
- The "Light" options provide a cleaner background for better visibility of transit lines.

## Key Files
- [gtfs_map_app.py](file:///c:/R_SMTR/projetos/mapas/codigos/gtfs_map_app.py): Main GUI logic.
- [gtfs_processor.py](file:///c:/R_SMTR/projetos/mapas/codigos/gtfs_processor.py): GTFS data handling.
- [README.md](file:///c:/R_SMTR/projetos/mapas/README.md): Project overview.
