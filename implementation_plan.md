# Implementation Plan - GTFS Map GUI

This project aims to create a Python desktop application that allows users to load GTFS files, select specific routes, customize their appearance on a map, and manage layer ordering.

## Proposed Changes

### [GTFS Map App Component]

#### [NEW] [GTFS Map App](file:///c:/R_SMTR/projetos/mapas/gtfs_map_app.py)

- **GTFS Loader**: Reads `shapes.txt`, `routes.txt`, and `trips.txt` from a ZIP file.
- **Data Model**: Stores route shapes as `geopandas` geometries or simple coordinate lists.
- **GUI (CustomTkinter)**:
    - Sidebar for route selection (searchable list).
    - Style controls (color picker, thickness slider).
    - Layer manager (move up/down, toggle visibility).
    - Basemap selector (OpenStreetMap, Satellite, etc.).
- **Map View (TkinterMapView)**:
    - Interactive map for horizontal/vertical navigation.
    - Dynamic rendering of selected routes with custom styles.

## Technology Stack
- `CustomTkinter` (Modern UI)
- `TkinterMapView` (Interactive Maps in Tkinter)
- `Pandas` / `GeoPandas` (Data Processing)
- `Shapely` (Geometry)

## Verification Plan

### Automated Tests
- No automated tests planned for this visual application.

### Manual Verification
1. Run `python gtfs_map_app.py`.
2. Load a sample GTFS zip file.
3. Select multiple routes and verify they appear on the map.
4. Change colors and thickness for each route.
5. Change layer order and verify overlap changes.
6. Switch between different basemaps.
