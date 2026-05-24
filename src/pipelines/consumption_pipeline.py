from typing import List, Dict, Optional
import duckdb

try:
    from ..utils.pipeline_classes import BasePipeline, BaseProcessor, BaseStorage
    from ..utils.api_client import fetch_with_pagination
    from ..utils.configuration_classes import ConfigurationManager
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from utils.pipeline_classes import BasePipeline, BaseProcessor, BaseStorage
    from utils.api_client import fetch_with_pagination
    from utils.configuration_classes import ConfigurationManager


class ConsumptionProcessor(BaseProcessor):
    """
    Processor for energy consumption data.
    """
    
    def __init__(self):
        super().__init__('consumption')
    
    def process(self, data: List[Dict]) -> List[Dict]:
        """
        Process consumption data (currently no transformation needed).
        
        Args:
            data: Raw consumption data
            
        Returns:
            Processed data (same as input for now)
        """
        return data


class ConsumptionStorage(BaseStorage):
    """
    Storage handler for consumption data.
    """
    
    def __init__(self):
        super().__init__('consumption')
    
    def create_table(self, conn: duckdb.DuckDBPyConnection) -> None:
        """
        Create the energy consumption table with proper schema.
        
        Args:
            conn: Database connection
        """
        conn.execute("DROP TABLE IF EXISTS consumption")
        
        # Get SQL from config
        config = self.config_manager.get_configuration_by_table('consumption')
        if config and config.sql_creation:
            conn.execute(config.sql_creation)
        else:
            # Fallback to hardcoded SQL
            conn.execute("""
                CREATE TABLE consumption (
                    date DATE,
                    time_slot STRING,
                    flag_ignore BOOLEAN,
                    datetime_str STRING,
                    electricity_status STRING,
                    gas_natran_status STRING,
                    gas_terega_status STRING,
                    total_consumption_mw INTEGER,
                    total_gas_consumption_mw INTEGER,
                    electricity_consumption_mw INTEGER,
                    gas_natran_consumption_mw INTEGER,
                    gas_terega_consumption_mw INTEGER
                )
            """)
    
    def insert_data(self, conn: duckdb.DuckDBPyConnection, data_file_path: str) -> int:
        """
        Insert consumption data into database.
        
        Args:
            conn: Database connection
            data_file_path: Path to JSON data file
            
        Returns:
            Number of records inserted
        """
        # Insert data from JSON
        conn.execute(f"""
            INSERT INTO consumption
            SELECT 
                CAST(Date AS DATE) as date,
                Heure::STRING as time_slot,
                flag_ignore::BOOLEAN as flag_ignore,
                "Date - Heure"::STRING as datetime_str,
                "Statut - RTE"::STRING as electricity_status,
                "Statut - NaTran"::STRING as gas_natran_status,
                "Statut - Teréga"::STRING as gas_terega_status,
                "Consommation brute totale (MW)"::INTEGER as total_consumption_mw,
                "Consommation brute gaz totale (MW PCS 0°C)"::INTEGER as total_gas_consumption_mw,
                "Consommation brute électricité (MW) - RTE"::INTEGER as electricity_consumption_mw,
                "Consommation brute gaz (MW PCS 0°C) - NaTran"::INTEGER as gas_natran_consumption_mw,
                "Consommation brute gaz (MW PCS 0°C) - Teréga"::INTEGER as gas_terega_consumption_mw
            FROM read_json('{data_file_path}')
        """)
        
        # Return count
        result = conn.execute("SELECT COUNT(*) as count FROM consumption").fetchone()
        return result[0] if result else 0


class ConsumptionPipeline(BasePipeline):
    """
    Complete pipeline for energy consumption data.
    Handles fetching from API, processing, and storage.
    """
    
    def __init__(self):
        super().__init__('consumption')
        self.processor = ConsumptionProcessor()
        self.storage = ConsumptionStorage()
    
    def fetch(self, start_date: str = None, end_date: str = None, single_date: str = None, **kwargs) -> List[Dict]:
        """
        Fetch energy consumption data from French government API.
        
        Args:
            start_date: Start date for range (YYYY-MM-DD format)
            end_date: End date for range (YYYY-MM-DD format)
            single_date: Single specific date (YYYY-MM-DD format)
            **kwargs: Additional parameters (ignored)
            
        Returns:
            List of consumption records
        """
        print("Fetching consumption data...")
        
        # Get configuration
        config = ConfigurationManager.get_configuration_by_table('consumption')
        if not config:
            raise ValueError("No configuration found for consumption table")
        
        # Get API URL from config property
        base_url = config.url
        
        # Determine query parameters
        if single_date:
            # Single date query
            params = {'Date__exact': f'"{single_date}"'}
            print(f"Fetching data for single date: {single_date}")
        else:
            # Date range query
            if not start_date:
                start_date = "2026-01-01"
            if not end_date:
                end_date = "2026-03-31"
                
            params = {
                'Date__greater': start_date,
                'Date__less': end_date
            }
            print(f"Fetching data for date range: {start_date} to {end_date}")
        
        try:
            data = fetch_with_pagination(base_url, params)
            print(f"Total consumption records collected: {len(data)}")
            return data
            
        except Exception as e:
            print(f"Error fetching data: {e}")
            return []
    
    def process(self, data: List[Dict]) -> List[Dict]:
        """
        Process consumption data.
        
        Args:
            data: Raw consumption data
            
        Returns:
            Processed data
        """
        return self.processor.process(data)
    
    def store(self, data: List[Dict], file_path: str = None) -> None:
        """
        Store consumption data to JSON file.
        
        Args:
            data: Processed data to store
            file_path: Optional custom file path
        """
        self.processor.save_to_file(data, file_path)
    
    def load_to_database(self, db_path: str = '../data/energy-analytics.db') -> None:
        """
        Load consumption data into database.
        
        Args:
            db_path: Path to database file
        """
        self.storage.load_to_database(db_path)