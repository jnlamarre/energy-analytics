from typing import Optional
import duckdb
import logging

try:
    from ..utils.pipelines import BasePipeline, BaseProcessor, BaseStorage
    from ..utils.api import fetch_paginated_api  # pragma: no cover
    from ..utils.configuration_classes import ConfigurationManager  # pragma: no cover
except ImportError:  # pragma: no cover
    import sys  # pragma: no cover
    import os  # pragma: no cover
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))  # pragma: no cover
    from utils.pipelines import BasePipeline, BaseProcessor, BaseStorage  # pragma: no cover
    from utils.api import fetch_paginated_api  # pragma: no cover
    from utils.configuration_classes import ConfigurationManager  # pragma: no cover


class StationsProcessor(BaseProcessor):
    """
    Processor for fuel station data with coordinate processing.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        super().__init__('stations', logger)
    
    def process(self, data: list[dict]) -> list[dict]:
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
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        super().__init__('stations', logger)
    
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
            
        self.logger.info(f"Loading station data from {data_file_path}...")
        
        # Check if data file has content before attempting bulk import
        import json
        try:
            with open(data_file_path, 'r', encoding='utf-8') as f:
                data_content = json.load(f)
                if not data_content:
                    self.logger.warning("No data to import (empty JSON file)")
                    return 0
        except (json.JSONDecodeError, FileNotFoundError, UnicodeDecodeError):
            self.logger.error("Cannot read data file or file is corrupted")
            return 0
        
        # Bulk import with field mapping from French to English names
        # Raw data approach: insert all records including duplicates
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
        self.logger.info(f"Loaded {count} station records")
        return count


class StationsPipeline(BasePipeline):
    """
    Complete pipeline for fuel station data.
    Handles fetching from API, processing, and storage.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        super().__init__('stations', logger)
        self.processor = StationsProcessor(logger)
        self.storage = StationsStorage(logger)
    
    def fetch(self, **kwargs) -> list[dict]:
        """
        Fetch fuel station data from French government API.
        
        Args:
            **kwargs: Additional parameters (ignored)
            
        Returns:
            List of fuel station records
        """
        self.logger.info("Fetching station data...")
        
        # Get configuration
        config = ConfigurationManager.get_configuration_by_table('stations')
        if not config:
            raise ValueError("No configuration found for stations table")
        
        # Get URL template from config property (includes {step} and {offset} placeholders)
        # Convert {step} to {limit} for fetch_paginated_api function
        url_template = config.url.replace('{step}', '{limit}')
        
        data = fetch_paginated_api(url_template, limit=100, max_records=10000)
        self.logger.info(f"Total stations fetched: {len(data)}")
        
        return data
    
    def process(self, data: list[dict]) -> list[dict]:
        """
        Process station data.
        
        Args:
            data: Raw station data
            
        Returns:
            Processed data
        """
        return self.processor.process(data)
    
    def store(self, data: list[dict], file_path: str | None = None) -> None:
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