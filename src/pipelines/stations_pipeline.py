from typing import List, Dict, Optional, Tuple
import duckdb

try:
    from ..utils.pipeline_classes import BasePipeline, BaseProcessor, BaseStorage
    from ..utils.api_client import fetch_paginated_api
    from ..utils.configuration_classes import ConfigurationManager
    from ..utils.file_handler import load_json
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from utils.pipeline_classes import BasePipeline, BaseProcessor, BaseStorage
    from utils.api_client import fetch_paginated_api
    from utils.configuration_classes import ConfigurationManager
    from utils.file_handler import load_json


class StationsProcessor(BaseProcessor):
    """
    Processor for fuel station data with coordinate processing.
    """
    
    def __init__(self):
        super().__init__('stations')
    
    def process_coordinates(self, latitude: str, longitude: str) -> Tuple[Optional[float], Optional[float]]:
        """
        Convert coordinate strings to float values with proper scaling.
        
        Args:
            latitude: Latitude as string
            longitude: Longitude as string
        
        Returns:
            Tuple of (lat, lon) as floats, or (None, None) if conversion fails
        """
        try:
            lat = float(latitude) / 100000 if latitude else None
            lon = float(longitude) / 100000 if longitude else None
            return lat, lon
        except (ValueError, TypeError):
            return None, None
    
    def process(self, data: List[Dict]) -> List[Dict]:
        """
        Process station data (currently no transformation needed beyond coordinate processing).
        
        Args:
            data: Raw station data
            
        Returns:
            Processed data (same as input for now)
        """
        return data


class StationsStorage(BaseStorage):
    """
    Storage handler for fuel station data.
    """
    
    def __init__(self):
        super().__init__('stations')
    
    def create_table(self, conn: duckdb.DuckDBPyConnection) -> None:
        """
        Create the fuel stations table with proper schema.
        
        Args:
            conn: Database connection
        """
        conn.execute("DROP TABLE IF EXISTS stations")
        
        # Get SQL from config
        config = self.config_manager.get_configuration_by_table('stations')
        if config and config.sql_creation:
            conn.execute(config.sql_creation)
        else:
            # Fallback to hardcoded SQL
            conn.execute("""
                CREATE TABLE stations (
                    id BIGINT PRIMARY KEY,
                    latitude DOUBLE,
                    longitude DOUBLE,
                    postal_code VARCHAR(10),
                    address VARCHAR(200),
                    city VARCHAR(100),
                    services_json TEXT,
                    hours_json TEXT,
                    
                    -- Diesel (Gazole)
                    gazole_price DECIMAL(5,3),
                    gazole_updated TIMESTAMPTZ,
                    
                    -- SP95
                    sp95_price DECIMAL(5,3),
                    sp95_updated TIMESTAMPTZ,
                    
                    -- SP98
                    sp98_price DECIMAL(5,3),
                    sp98_updated TIMESTAMPTZ
                )
            """)
    
    def process_coordinates(self, latitude: str, longitude: str) -> Tuple[Optional[float], Optional[float]]:
        """
        Convert coordinate strings to float values with proper scaling.
        
        Args:
            latitude: Latitude as string
            longitude: Longitude as string
        
        Returns:
            Tuple of (lat, lon) as floats, or (None, None) if conversion fails
        """
        try:
            lat = float(latitude) / 100000 if latitude else None
            lon = float(longitude) / 100000 if longitude else None
            return lat, lon
        except (ValueError, TypeError):
            return None, None
    
    def insert_data(self, conn: duckdb.DuckDBPyConnection, data_file_path: str) -> int:
        """
        Insert station data into database.
        
        Args:
            conn: Database connection
            data_file_path: Path to JSON data file
            
        Returns:
            Number of records inserted
        """
        # Load data from JSON
        data = load_json(data_file_path)
        print(f"Processing {len(data)} stations...")
        
        inserted_count = 0
        
        # Insert data
        for station in data:
            try:
                lat, lon = self.process_coordinates(
                    station.get('latitude'), 
                    station.get('longitude')
                )
                
                conn.execute("""
                    INSERT INTO stations (
                        id, latitude, longitude, postal_code, address, city,
                        services_json, hours_json,
                        gazole_price, gazole_updated,
                        sp95_price, sp95_updated,
                        sp98_price, sp98_updated
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, [
                    station.get('id'),
                    lat,
                    lon,
                    station.get('cp'),
                    station.get('adresse'),
                    station.get('ville'),
                    station.get('services'),
                    station.get('horaires'),
                    station.get('gazole_prix'),
                    station.get('gazole_maj'),
                    station.get('sp95_prix'),
                    station.get('sp95_maj'),
                    station.get('sp98_prix'),
                    station.get('sp98_maj')
                ])
                inserted_count += 1
                
            except Exception as e:
                print(f"Error inserting station {station.get('id')}: {e}")
                continue
        
        return inserted_count


class StationsPipeline(BasePipeline):
    """
    Complete pipeline for fuel station data.
    Handles fetching from API, processing, and storage.
    """
    
    def __init__(self):
        super().__init__('stations')
        self.processor = StationsProcessor()
        self.storage = StationsStorage()
    
    def fetch(self, **kwargs) -> List[Dict]:
        """
        Fetch fuel station data from French government API.
        
        Args:
            **kwargs: Additional parameters (ignored)
            
        Returns:
            List of fuel station records
        """
        print("Fetching station data...")
        
        # Get configuration
        config = ConfigurationManager.get_configuration_by_table('stations')
        if not config:
            raise ValueError("No configuration found for stations table")
        
        # Get URL template from config property (already includes {step} and {offset} placeholders)
        url_template = config.url.replace('{step}', '{limit}')
        
        data = fetch_paginated_api(url_template)
        print(f"Total stations fetched: {len(data)}")
        
        return data
    
    def process(self, data: List[Dict]) -> List[Dict]:
        """
        Process station data.
        
        Args:
            data: Raw station data
            
        Returns:
            Processed data
        """
        return self.processor.process(data)
    
    def store(self, data: List[Dict], file_path: str = None) -> None:
        """
        Store station data to JSON file.
        
        Args:
            data: Processed data to store
            file_path: Optional custom file path
        """
        self.processor.save_to_file(data, file_path)
    
    def load_to_database(self, db_path: str = '../data/energy-analytics.db') -> None:
        """
        Load station data into database.
        
        Args:
            db_path: Path to database file
        """
        self.storage.load_to_database(db_path)