from typing import List, Dict, Optional
import duckdb

try:
    from ..utils.pipeline_classes import BasePipeline, BaseProcessor, BaseStorage
    from ..utils.api_client import fetch_paginated_api
    from ..utils.configuration_classes import ConfigurationManager
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from utils.pipeline_classes import BasePipeline, BaseProcessor, BaseStorage
    from utils.api_client import fetch_paginated_api
    from utils.configuration_classes import ConfigurationManager


class StationsProcessor(BaseProcessor):
    """
    Processor for fuel station data with coordinate processing.
    """
    
    def __init__(self):
        super().__init__('stations')
    
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
    
    def insert_data(self, conn: duckdb.DuckDBPyConnection, data_file_path: str) -> int:
        """
        Insert station data into database using bulk import with field mapping.
        
        Args:
            conn: Database connection
            data_file_path: Path to JSON data file
            
        Returns:
            Number of records inserted
        """
        import os
        
        # Basic error checking
        if not os.path.exists(data_file_path):
            raise FileNotFoundError(f"Data file not found: {data_file_path}")
            
        print(f"Loading station data from {data_file_path}...")
        
        # Bulk import with field mapping from French to English names
        conn.execute(f"""
            INSERT INTO stations (
                id, latitude, longitude, postal_code, address, city,
                services_json, hours_json,
                gazole_price, gazole_updated,
                sp95_price, sp95_updated,
                sp98_price, sp98_updated
            )
            SELECT 
                id,
                latitude,
                longitude,
                cp as postal_code,
                adresse as address,
                ville as city,
                services as services_json,
                horaires as hours_json,
                gazole_prix as gazole_price,
                gazole_maj as gazole_updated,
                sp95_prix as sp95_price,
                sp95_maj as sp95_updated,
                sp98_prix as sp98_price,
                sp98_maj as sp98_updated
            FROM read_json_auto('{data_file_path}')
        """)
        
        # Get count of records in table
        count = conn.execute("SELECT COUNT(*) FROM stations").fetchone()[0]
        print(f"Loaded {count} station records")
        return count


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