import pandas as pd
import zipfile
import os

class GTFSProcessor:
    def __init__(self, zip_path):
        self.zip_path = zip_path
        self.routes = pd.DataFrame()
        self.trips = pd.DataFrame()
        self.shapes = pd.DataFrame()
        self.coords_cache = {}  # Cache: {shape_id: [(lat, lon), ...]}
        self.load_data()

    def load_data(self):
        """Loads essential GTFS files from the ZIP."""
        with zipfile.ZipFile(self.zip_path, 'r') as z:
            # Load routes
            if 'routes.txt' in z.namelist():
                with z.open('routes.txt') as f:
                    self.routes = pd.read_csv(f, dtype={'route_id': str, 'route_short_name': str, 'route_long_name': str}, 
                                            encoding='utf-8-sig', on_bad_lines='skip')
            
            # Load trips (to link routes to shapes and get headsigns/directions)
            if 'trips.txt' in z.namelist():
                with z.open('trips.txt') as f:
                    self.trips = pd.read_csv(f, dtype={'route_id': str, 'trip_id': str, 'shape_id': str, 'trip_headsign': str, 'direction_id': str}, 
                                           encoding='utf-8-sig', on_bad_lines='skip')
            
            # Load shapes
            if 'shapes.txt' in z.namelist():
                with z.open('shapes.txt') as f:
                    self.shapes = pd.read_csv(f, dtype={'shape_id': str}, 
                                            encoding='utf-8-sig', on_bad_lines='skip')
                    # Sort by sequence
                    self.shapes['shape_pt_sequence'] = pd.to_numeric(self.shapes['shape_pt_sequence'], errors='coerce').fillna(0).astype(int)
                    self.shapes.sort_values(['shape_id', 'shape_pt_sequence'], inplace=True)

    def get_route_list(self):
        """Returns a list of routes with short name, headsign, and direction."""
        if self.routes.empty or self.trips.empty:
            return []
        
        # Merge trips with routes
        trips_info = self.trips[['route_id', 'shape_id', 'trip_headsign', 'direction_id']].drop_duplicates(subset=['shape_id'])
        merged = self.routes.merge(trips_info, on='route_id', how='inner')
        
        route_list = []
        for _, row in merged.iterrows():
            short_name = str(row['route_short_name'])
            headsign = str(row.get('trip_headsign', ''))
            direction = str(row.get('direction_id', ''))
            
            # Map direction_id to Ida/Volta (standard is 0/1)
            dir_label = ""
            if direction == '0': dir_label = "(Ida)"
            elif direction == '1': dir_label = "(Volta)"
            
            clean_headsign = headsign if headsign and headsign != 'nan' else ""
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

    def get_shape_coordinates(self, shape_id):
        """Returns a list of (lat, lon) tuples for a given shape_id with caching."""
        if shape_id in self.coords_cache:
            return self.coords_cache[shape_id]
            
        if self.shapes.empty:
            return []
        
        shape_data = self.shapes[self.shapes['shape_id'] == shape_id]
        if shape_data.empty:
            return []
        
        coords = list(zip(shape_data['shape_pt_lat'], shape_data['shape_pt_lon']))
        self.coords_cache[shape_id] = coords
        return coords
