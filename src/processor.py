import pandas as pd
import zipfile
import os
import logging
from typing import List, Dict, Tuple, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GTFSProcessor:
    """
    Handles loading and processing of GTFS data from a ZIP file.
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
        self.shapes = pd.DataFrame()
        self.coords_cache: Dict[str, List[Tuple[float, float]]] = {}
        self.load_data()

    def load_data(self) -> None:
        """
        Loads essential GTFS files (routes.txt, trips.txt, shapes.txt) from the ZIP.
        """
        if not os.path.exists(self.zip_path):
            logger.error(f"GTFS file not found: {self.zip_path}")
            raise FileNotFoundError(f"GTFS file not found: {self.zip_path}")

        try:
            with zipfile.ZipFile(self.zip_path, 'r') as z:
                file_list = z.namelist()
                
                # Load routes
                if 'routes.txt' in file_list:
                    with z.open('routes.txt') as f:
                        self.routes = pd.read_csv(f, dtype={'route_id': str, 'route_short_name': str, 'route_long_name': str}, 
                                                encoding='utf-8-sig', on_bad_lines='skip')
                    logger.info(f"Loaded {len(self.routes)} routes.")
                
                # Load trips
                if 'trips.txt' in file_list:
                    with z.open('trips.txt') as f:
                        self.trips = pd.read_csv(f, dtype={'route_id': str, 'trip_id': str, 'shape_id': str, 'trip_headsign': str, 'direction_id': str}, 
                                               encoding='utf-8-sig', on_bad_lines='skip')
                    logger.info(f"Loaded {len(self.trips)} trips.")
                
                # Load shapes
                if 'shapes.txt' in file_list:
                    with z.open('shapes.txt') as f:
                        self.shapes = pd.read_csv(f, dtype={'shape_id': str}, 
                                                encoding='utf-8-sig', on_bad_lines='skip')
                        if not self.shapes.empty:
                            self.shapes['shape_pt_sequence'] = pd.to_numeric(self.shapes['shape_pt_sequence'], errors='coerce').fillna(0).astype(int)
                            self.shapes.sort_values(['shape_id', 'shape_pt_sequence'], inplace=True)
                    logger.info(f"Loaded {len(self.shapes)} shape points.")
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
            logger.warning("Routes or trips data is empty.")
            return []
        
        # Merge trips with routes to find associated shape_ids
        # We drop duplicates to get unique shape_id/route_id combinations
        trips_info = self.trips[['route_id', 'shape_id', 'trip_headsign', 'direction_id']].drop_duplicates(subset=['shape_id'])
        merged = self.routes.merge(trips_info, on='route_id', how='inner')
        
        route_list = []
        for _, row in merged.iterrows():
            short_name = str(row['route_short_name'])
            headsign = str(row.get('trip_headsign', ''))
            direction = str(row.get('direction_id', ''))
            
            # Map direction_id to descriptive label
            dir_label = ""
            if direction == '0':
                dir_label = "(Ida)"
            elif direction == '1':
                dir_label = "(Volta)"
            
            clean_headsign = headsign if headsign and headsign.lower() != 'nan' else ""
            display_name = f"{short_name} - {clean_headsign} {dir_label}".strip(' - ')
            
            route_list.append({
                'route_id': row['route_id'],
                'shape_id': row['shape_id'],
                'display_name': display_name,
                'short_name': short_name,
                'long_name': str(row.get('route_long_name', '')),
                'direction': dir_label,
                'trip_headsign': headsign
            })
        
        return sorted(route_list, key=lambda x: x['display_name'])

    def get_shape_coordinates(self, shape_id: str) -> List[Tuple[float, float]]:
        """
        Gets the latitude and longitude coordinates for a given shape_id.

        Args:
            shape_id: The ID of the shape to retrieve.

        Returns:
            A list of (latitude, longitude) tuples.
        """
        if shape_id in self.coords_cache:
            return self.coords_cache[shape_id]
            
        if self.shapes.empty:
            return []
        
        shape_data = self.shapes[self.shapes['shape_id'] == shape_id]
        if shape_data.empty:
            logger.warning(f"No coordinates found for shape_id: {shape_id}")
            return []
        
        coords = list(zip(shape_data['shape_pt_lat'], shape_data['shape_pt_lon']))
        self.coords_cache[shape_id] = coords
        return coords
