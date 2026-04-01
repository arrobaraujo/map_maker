# GTFS Map Maker

[**Versão em Português**](README_PT.md)

GTFS route map generator with a modern graphical interface and GIS support.

- Architecture: [ARCHITECTURE.md](ARCHITECTURE.md)
- Contributing: [CONTRIBUTING.md](CONTRIBUTING.md)

## 📥 Download (Ready-to-use Version)

If you just want to run the app without installing Python:
1. Go to the [**Releases**](https://github.com/arrobaraujo/map_maker/releases) tab of this repository.
2. Download the latest `.exe` file at the bottom of the page in the "Assets" section.
3. Run the file directly! (If Windows blocks it, see [this guide](DISTRIBUTION_EN.md)).

## ✨ Features
- **Granular Zoom (0.1)**: Precise zoom adjustment for perfect framing, smooth and without jerky jumps.
- **Smart Multi-Selection**: Select multiple layers with **Ctrl + Click** or a full line (all directions) with **Shift + Click**.
- **Batch Styling**: Change color and thickness of multiple selected layers simultaneously.
- **Smart Legend:** Automatic unification by color to simplify visualization.
- Individual Layer Removal via button (✕).
- Clean screenshots (automatically hides zoom buttons).
- **High-Quality Export:** DPI control for sharp images and PDFs.
- **Professional Export:** Save selected routes in **SVG (Vector)**, **KML (Google Earth)**, **GeoPackage (.gpkg)**, and **Shapefile (.shp)** formats.

## Dependencies
- Python 3.9+
- CustomTkinter
- TkinterMapView

## 🚀 Running from Source

1. Ensure you have Python 3.10+ installed.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python src/app.py
   ```

## 🐳 Running with Docker

The project includes a GUI-enabled container using Xvfb + VNC + noVNC.

1. Build and start the container:
   ```bash
   docker compose up --build
   ```
2. Open the app in your browser:
   - http://localhost:6080/vnc.html
3. Optional direct VNC access:
   - Host: `localhost`
   - Port: `5901`

Notes:
- The `map_tiles_cache` folder is mounted as a volume to preserve tile cache.
- The Docker runtime is intended for development and demo usage.

## 📦 Building the Executable (.exe)

To create a single `.exe` file for Windows:

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```
2. Build using the provided script:
   ```powershell
   .\scripts\build_exe.ps1 -Clean
   ```
   Or run PyInstaller directly:
   ```bash
   pyinstaller app.spec
   ```
3. The final file will be in the `dist/` folder.

## 📂 Project Structure

- `src/`: Source code.
  - `app.py`: Main interface (GUI).
  - `processor.py`: GTFS logic.
  - `utils/renderer.py`: Map rendering.
- `tests/`: Automated tests (`pytest`).
- `map_tiles_cache/`: Offline map cache.
