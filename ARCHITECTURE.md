# Architecture - GTFS Map Maker

Internal structure, data flow, and design decisions.

---

## Project Structure

```text
map_maker/
├── src/
│   ├── app.py                  # GUI entry point
│   ├── processor.py            # GTFS processing and indexing
│   └── utils/
│       └── renderer.py         # Map rendering and geometry simplification
├── tests/
│   └── test_processor.py
├── map_tiles_cache/            # Local map tile cache (SQLite)
├── requirements.txt
├── app.spec                    # PyInstaller spec
├── LICENSE
├── README.md / README_PT.md
├── CONTRIBUTING.md / CONTRIBUTING_PT.md
├── ARCHITECTURE.md / ARCHITECTURE_PT.md
├── DISTRIBUTION_EN.md / DISTRIBUTION_PT.md
└── RELEASE_NOTES.md
```

---

## Modules and Responsibilities

### src/app.py - GUI

- GTFSMapApp: main application class.
- setup_ui(): builds sidebar, map area, controls, and legend.
- load_gtfs(): opens file picker and loads GTFS in a background thread.
- toggle_route(): adds/removes route layers on the map.
- select_layer(): supports single selection plus Ctrl/Shift multi-select behavior.
- redraw_all_paths(): redraws layers preserving order and style.
- save_map(): exports current map to PNG, PDF, or SVG with DPI options.
- export_sig(): exports active layers as GeoPackage, Shapefile, or KML.
- update_legend(): renders grouped floating legend.

Design highlights:

- Virtual scrolling for large route lists.
- Batch style editing for selected layers.
- Fractional zoom control with 0.1 increments.
- High DPI awareness for Windows.

### src/processor.py - GTFS engine

- GTFSProcessor: loads GTFS ZIP and indexes shape points.
- _setup_db(): creates temporary SQLite schema/index.
- load_data(): parses routes.txt, trips.txt, and shapes.txt.
- get_route_list(): merges GTFS metadata for route list UI.
- get_shape_coordinates(): reads ordered coordinates from SQLite.
- close(): closes DB and removes temp file.

Design highlights:

- Temporary SQLite storage keeps RAM usage low for large GTFS feeds.
- Chunk processing for shapes.txt.
- atexit cleanup for temporary resources.

### src/utils/renderer.py - Rendering utilities

- simplify_path(): Douglas-Peucker coordinate simplification.
- render_transparent_map(): transparent render pipeline with manual projection.
- _draw_legend(): legend rendering for exported images.

Design highlights:

- Simplification used for both interactive drawing and exports.
- Manual projection via decimal_to_osm to align exports with map viewport.

---

## Data Flow

1. User selects a GTFS ZIP file.
2. GTFSProcessor parses routes and trips to DataFrames.
3. shapes.txt coordinates are indexed in temporary SQLite.
4. App UI shows route list.
5. Selecting a route fetches coordinates, optionally simplifies them, and draws map paths.
6. Export operations convert active layers to raster/vector/GIS outputs.

---

## Technology Stack

- GUI: CustomTkinter
- Map widget: TkinterMapView
- Tabular data: Pandas
- GIS export: GeoPandas + Shapely + pyogrio
- Temporary storage: SQLite
- Imaging/export: Pillow
- Packaging: PyInstaller
- Tests: pytest

---

## Design Decisions

### Why SQLite for shapes

Large GTFS feeds can include millions of points. SQLite provides efficient indexed lookup by shape_id while keeping memory usage stable.

### Why virtual scrolling for route list

Rendering thousands of GUI widgets at once causes lag. Virtualized button pooling keeps the interface responsive with large route sets.

### Why Douglas-Peucker simplification

Complex routes with many points can slow rendering. Simplification preserves visual fidelity while reducing drawing load.

### Why manual SVG projection

Manual projection ensures exported vectors align with the exact map viewport currently shown in the UI.

---

## Distribution

Build executable using:

```bash
pyinstaller app.spec
```

Output binary is generated under dist/.

---

## Testing

Current tests are under tests/ and focus on processor behavior.

Run tests:

```bash
pytest tests/ -v
```
