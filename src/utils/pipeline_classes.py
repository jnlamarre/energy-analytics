from typing import Optional
from abc import ABC, abstractmethod


class BasePipeline(ABC):
    """
    Abstract base class for data pipelines.
    Defines the common interface for fetch -> process -> store operations.
    """
    
    def __init__(self, table_name: str):
        """
        Initialize pipeline with table name.
        
        Args:
            table_name: Name of the database table
        """
        self.table_name = table_name
    
    @abstractmethod
    def fetch(self, **kwargs) -> list[dict]:
        """
        Fetch data from external API.
        
        Args:
            **kwargs: Fetch parameters (dates, limits, etc.)
            
        Returns:
            List of fetched records
        """
        pass
    
    @abstractmethod
    def process(self, data: list[dict]) -> list[dict]:
        """
        Process and transform the fetched data.
        
        Args:
            data: Raw data from API
            
        Returns:
            Processed data ready for storage
        """
        pass
    
    @abstractmethod
    def store(self, data: list[dict], file_path: str | None = None) -> None:
        """
        Store processed data to JSON file.
        
        Args:
            data: Processed data to store
            file_path: Optional custom file path
        """
        pass
    
    @abstractmethod
    def load_to_database(self, db_path: str = '../data/energy-analytics.db') -> None:
        """
        Load data from JSON file into database.
        
        Args:
            db_path: Path to database file
        """
        pass
    
    def run_full_pipeline(self, db_path: str = '../data/energy-analytics.db', **fetch_kwargs) -> None:
        """
        Execute the complete pipeline: fetch -> process -> store -> load to DB.
        
        Args:
            db_path: Path to database file
            **fetch_kwargs: Arguments for the fetch method
        """
        print(f"Starting {self.__class__.__name__} pipeline...")
        
        # Fetch data
        raw_data = self.fetch(**fetch_kwargs)
        print(f"Fetched {len(raw_data)} records")
        
        # Process data
        processed_data = self.process(raw_data)
        print(f"Processed {len(processed_data)} records")
        
        # Store to file
        self.store(processed_data)
        
        # Load to database
        self.load_to_database(db_path)
        
        print(f"{self.__class__.__name__} pipeline completed successfully!")


class BaseProcessor:
    """
    Base class for data processors with common functionality.
    """
    
    def __init__(self, table_name: str):
        """
        Initialize processor with table name.
        
        Args:
            table_name: Name of the database table
        """
        self.table_name = table_name
        
        try:
            from ..utils.file_handler import save_json
            from ..utils.configuration_classes import ConfigurationManager
            self.save_json = save_json
            self.config_manager = ConfigurationManager
        except ImportError:
            from utils.file_handler import save_json
            from utils.configuration_classes import ConfigurationManager
            self.save_json = save_json
            self.config_manager = ConfigurationManager
    
    def save_to_file(self, data: list[dict], file_path: str | None = None) -> None:
        """
        Save data to JSON file using configuration.
        
        Args:
            data: Data to save
            file_path: Optional custom file path
        """
        if file_path is None:
            config = self.config_manager.get_configuration_by_table(self.table_name)
            if not config:
                raise ValueError(f"No configuration found for {self.table_name} table")
            file_path = config.target_file
            
        print(f"Saving {self.table_name} data to JSON file...")
        self.save_json(data, file_path)
        print(f"Data saved to {file_path}")


class BaseStorage:
    """
    Base class for database storage with common functionality.
    """
    
    def __init__(self, table_name: str):
        """
        Initialize storage with table name.
        
        Args:
            table_name: Name of the database table
        """
        self.table_name = table_name
        
        try:
            from ..utils.database import get_connection, DuckDBConnection
            from ..utils.configuration_classes import ConfigurationManager
            self.get_connection = get_connection
            self.DuckDBConnection = DuckDBConnection
            self.config_manager = ConfigurationManager
        except ImportError:
            from utils.database import get_connection, DuckDBConnection
            from utils.configuration_classes import ConfigurationManager
            self.get_connection = get_connection
            self.DuckDBConnection = DuckDBConnection
            self.config_manager = ConfigurationManager
    
    @abstractmethod
    def create_table(self, conn) -> None:
        """
        Create the database table.
        
        Args:
            conn: Database connection
        """
        pass
    
    @abstractmethod
    def insert_data(self, conn, data_file_path: str) -> int:
        """
        Insert data into the database table.
        
        Args:
            conn: Database connection
            data_file_path: Path to JSON data file
            
        Returns:
            Number of records inserted
        """
        pass
    
    def load_to_database(self, db_path: str = '../data/energy-analytics.db') -> None:
        """
        Load data from JSON file into database.
        
        Args:
            db_path: Path to database file
        """
        print(f"Loading {self.table_name} data into database...")
        
        with self.DuckDBConnection(db_path) as conn:
            # Create table
            self.create_table(conn)
            
            # Get data file path from config
            config = self.config_manager.get_configuration_by_table(self.table_name)
            if not config:
                raise ValueError(f"No configuration found for {self.table_name} table")
            
            data_file_path = config.target_file
            
            # Insert data
            record_count = self.insert_data(conn, data_file_path)
            print(f"Successfully loaded {record_count} records")
            
        print("Database loading completed!")