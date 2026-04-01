import pandas as pd
import zipfile
import os
import logging
import sqlite3
import tempfile
import atexit
from typing import List, Dict, Tuple, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GTFSProcessor:
    """
    Handles loading and processing of GTFS data from a ZIP file.
    Uses SQLite for efficient geometric data storage.
    """
    def __init__(self, zip_path: str):
        """
        Initializes the processor and loads essential GTFS data.

        Args:
            zip_path: Path to the GTFS ZIP file.
        """
        self.zip_path = zip_path
        self.routes = pd.DataFrame()
        self.trips = pd.DataFrame()
        
        # Setup temporary SQLite database for shapes to save RAM
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.db_path = self.temp_db.name
        self.temp_db.close()
        
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._closed = False
        self._setup_db()
        
        atexit.register(lambda: self.close())
        
        self.load_data()

    def _setup_db(self):
        """Creates the necessary tables and indexes in the temporary SQLite DB."""
        self.cursor.execute("DROP TABLE IF EXISTS shapes")
        self.cursor.execute("""
            CREATE TABLE shapes (
                shape_id TEXT,
                lat REAL,
                lon REAL,
                sequence INTEGER
            )
        """)
        self.cursor.execute("CREATE INDEX idx_shape_id ON shapes (shape_id)")
        self.conn.commit()

    def load_data(self) -> None:
        """
        Loads essential GTFS files (routes.txt, trips.txt, shapes.txt) from the ZIP.
        Simplified to only load metadata to RAM and points to SQLite.
        """
        if not os.path.exists(self.zip_path):
            logger.error(f"GTFS file not found: {self.zip_path}")
            raise FileNotFoundError(f"GTFS file not found: {self.zip_path}")

        try:
            with zipfile.ZipFile(self.zip_path, 'r') as z:
                file_list = z.namelist()

                required_files = {'routes.txt', 'trips.txt', 'shapes.txt'}
                missing = sorted(required_files.difference(file_list))
                if missing:
                    missing_csv = ", ".join(missing)
                    raise ValueError(f"Invalid GTFS ZIP. Missing required files: {missing_csv}")
                
                # Load routes - Include colors
                with z.open('routes.txt') as f:
                    available_cols = pd.read_csv(f, nrows=0).columns
                with z.open('routes.txt') as f:
                    use_cols = [c for c in ['route_id', 'route_short_name', 'route_long_name', 'route_color', 'route_text_color'] if c in available_cols]
                    self.routes = pd.read_csv(f, usecols=use_cols, dtype={'route_id': str, 'route_short_name': str}, 
                                            encoding='utf-8-sig', on_bad_lines='skip')
                logger.info(f"Loaded {len(self.routes)} routes.")
                
                # Load trips - Only essential columns
                with z.open('trips.txt') as f:
                    available_cols = pd.read_csv(f, nrows=0).columns
                with z.open('trips.txt') as f:
                    use_cols = [c for c in ['route_id', 'trip_id', 'shape_id', 'trip_headsign', 'direction_id'] if c in available_cols]
                    self.trips = pd.read_csv(f, usecols=use_cols, dtype={'route_id': str, 'shape_id': str}, 
                                           encoding='utf-8-sig', on_bad_lines='skip')
                logger.info(f"Loaded {len(self.trips)} trips.")
                
                # Load shapes -> DIRECT TO SQLITE
                logger.info("Processing shapes into SQLite (this may take a moment for large files)...")
                with z.open('shapes.txt') as f:
                    # Process in chunks to keep memory low
                    chunk_iter = pd.read_csv(f, chunksize=100000, dtype={'shape_id': str}, encoding='utf-8-sig')
                    for chunk in chunk_iter:
                        # Map essential columns
                        available_cols = chunk.columns
                        mapping = {
                            'shape_id': 'shape_id',
                            'shape_pt_lat': 'lat',
                            'shape_pt_lon': 'lon',
                            'shape_pt_sequence': 'sequence'
                        }
                        data_to_insert = chunk[[c for c in mapping.keys() if c in available_cols]].rename(columns=mapping)
                        data_to_insert.to_sql('shapes', self.conn, if_exists='append', index=False)
                
                self.conn.commit()
                logger.info("Shapes indexed in SQLite.")
        except Exception as e:
            logger.error(f"Error loading GTFS data: {e}")
            raise

    def get_route_list(self) -> List[Dict]:
        """
        Returns a processed list of routes with display names and metadata.

        Returns:
            A list of dictionaries, each representing a route.
        """
        if self.routes.empty or self.trips.empty:
            return []
        
        trips_info = self.trips[['route_id', 'shape_id', 'trip_headsign', 'direction_id']].drop_duplicates(subset=['shape_id'])
        merged = self.routes.merge(trips_info, on='route_id', how='inner')
        
        route_list = []
        for _, row in merged.iterrows():
            short_name = str(row.get('route_short_name', ''))
            headsign = str(row.get('trip_headsign', ''))
            direction = str(row.get('direction_id', ''))
            dir_label = "(Ida)" if direction == '0' else ("(Volta)" if direction == '1' else "")
            
            clean_headsign = headsign if headsign and headsign.lower() != 'nan' else ""
            display_name = f"{short_name} - {clean_headsign} {dir_label}".strip(' - ')
            
            route_list.append({
                'route_id': row['route_id'],
                'shape_id': row['shape_id'],
                'display_name': display_name,
                'short_name': short_name,
                'long_name': str(row.get('route_long_name', '')),
                'direction': dir_label,
                'trip_headsign': headsign,
                'route_color': str(row.get('route_color', '')),
                'route_text_color': str(row.get('route_text_color', ''))
            })
        
        return sorted(route_list, key=lambda x: x['display_name'])

    def get_shape_coordinates(self, shape_id: str) -> List[Tuple[float, float]]:
        """
        Gets the latitude and longitude coordinates for a given shape_id from SQLite.
        """
        self.cursor.execute("SELECT lat, lon FROM shapes WHERE shape_id = ? ORDER BY sequence", (shape_id,))
        return self.cursor.fetchall()

    def close(self):
        """Closes the DB connection and removes the temporary file."""
        if self._closed:
            return
        try:
            if hasattr(self, 'conn'):
                self.conn.close()
            if hasattr(self, 'db_path') and os.path.exists(self.db_path):
                os.remove(self.db_path)
                logger.info("Temporary shapes database removed.")
        except Exception as e:
            logger.error(f"Error closing GTFSProcessor: {e}")
        finally:
            self._closed = True
