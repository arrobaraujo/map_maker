# GTFS Map Maker

[**Versão em Português**](README.md)

GTFS route map generator with a modern graphical interface and GIS support.

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

## 📦 Building the Executable (.exe)

To create a single `.exe` file for Windows:

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```
2. Generate the executable (adjust the `.venv` path if necessary):
   ```bash
   pyinstaller --noconsole --onefile --add-data ".venv/Lib/site-packages/customtkinter;customtkinter/" src/app.py
   ```
3. The final file will be in the `dist/` folder.

## 📂 Project Structure

- `src/`: Source code.
  - `app.py`: Main interface (GUI).
  - `processor.py`: GTFS logic.
  - `utils/renderer.py`: Map rendering.
- `tests/`: Automated tests (`pytest`).
- `map_tiles_cache/`: Offline map cache.
