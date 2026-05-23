from typing import Dict, Any, List
import json
import os


class BaseConfiguration:
    """
    Base configuration class for API data sources.
    """
    
    def __init__(self, config_dict: Dict[str, Any]):
        """
        Initialize configuration from dictionary.
        
        Args:
            config_dict: Configuration dictionary from JSON
        """
        self.config = config_dict
        self.table_name = config_dict.get('nom_table')
        self.dataset = config_dict.get('dataset')
        self.api_type = config_dict.get('type_api')
        self.target_file = config_dict.get('fichier_cible')
        self.sql_file = config_dict.get('fichier_sql')
        self.sql_creation = config_dict.get('sql_creation')
    
    def load_sql_schema(self) -> None:
        """
        Load SQL schema from file and store in sql_creation attribute.
        """
        if self.sql_file:
            sql_path = os.path.join(os.path.dirname(__file__), '..', 'sql', self.sql_file)
            with open(sql_path, 'r', encoding='utf-8') as f:
                self.sql_creation = f.read()
    
    @classmethod
    def create_from_dict(cls, config_dict: Dict[str, Any]) -> 'BaseConfiguration':
        """
        Factory method to create appropriate configuration object.
        
        Args:
            config_dict: Configuration dictionary from JSON
            
        Returns:
            Configuration object instance
            
        Raises:
            ValueError: If API type is not supported
        """
        # Load SQL content
        if 'fichier_sql' in config_dict:
            sql_path = os.path.join(os.path.dirname(__file__), '..', 'sql', config_dict['fichier_sql'])
            with open(sql_path, 'r', encoding='utf-8') as f:
                config_dict['sql_creation'] = f.read()
        
        api_type = config_dict.get('type_api')
        
        if api_type == 'data_gouv':
            return DataGouvConfiguration(config_dict)
        elif api_type == 'economie_gouv':
            return EconomieGouvConfiguration(config_dict)
        else:
            raise ValueError(f"Unsupported API type: {api_type}")
    
    def build_url(self, **kwargs) -> str:
        """
        Build API URL with given parameters.
        
        Args:
            **kwargs: URL parameters
            
        Returns:
            Complete API URL
            
        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement build_url method")


class DataGouvConfiguration(BaseConfiguration):
    """
    Configuration for data.gouv.fr Tabular API.
    Used for energy consumption data.
    """
    
    def build_url(self, **kwargs) -> str:
        """
        Build Tabular API URL.
        
        Returns:
            Complete API URL for data.gouv.fr tabular API
        """
        return f'https://tabular-api.data.gouv.fr/api/resources/{self.dataset}/data/'


class EconomieGouvConfiguration(BaseConfiguration):
    """
    Configuration for data.economie.gouv.fr OpenData API.
    Used for fuel station price data.
    """
    
    def build_url(self, limit: int = 100, offset: int = 0, **kwargs) -> str:
        """
        Build OpenData API URL with pagination and selection parameters.
        
        Args:
            limit: Number of records per page
            offset: Starting offset for pagination
            **kwargs: Additional parameters (ignored)
            
        Returns:
            Complete API URL for economie.gouv.fr API
        """
        base_url = f'https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/{self.dataset}/records'
        
        # Add select parameters for fuel station data
        if 'prix-des-carburants' in self.dataset:
            select_params = 'id%2Clatitude%2Clongitude%2Ccp%2Cadresse%2Cville%2Cservices%2Cgazole_prix%2Cgazole_maj%2Choraires%2Csp95_maj%2Csp95_prix%2Csp98_maj%2Csp98_prix'
            base_url += f'?select={select_params}'
            base_url += f'&limit={limit}&offset={offset}'
        
        return base_url


class ConfigurationManager:
    """
    Manager class for loading and managing configurations.
    """
    
    @classmethod
    def load_all_configurations(cls, config_file: str = 'config.json') -> List[BaseConfiguration]:
        """
        Load all configurations from JSON file.
        
        Args:
            config_file: Name of the configuration file
            
        Returns:
            List of configuration objects
        """
        config_path = os.path.join(os.path.dirname(__file__), config_file)
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config_dicts = json.load(f)
        
        return [BaseConfiguration.create_from_dict(config) for config in config_dicts]
    
    @classmethod
    def get_configuration_by_table(cls, table_name: str) -> BaseConfiguration:
        """
        Get configuration object for a specific table.
        
        Args:
            table_name: Name of the table to get config for
            
        Returns:
            Configuration object or None if not found
        """
        configurations = cls.load_all_configurations()
        
        for config in configurations:
            if config.table_name == table_name:
                return config
        
        return None
    
    @classmethod
    def get_configurations_by_api_type(cls, api_type: str) -> List[BaseConfiguration]:
        """
        Get all configurations for a specific API type.
        
        Args:
            api_type: Type of API ('data_gouv' or 'economie_gouv')
            
        Returns:
            List of configuration objects for the specified API type
        """
        configurations = cls.load_all_configurations()
        
        return [config for config in configurations if config.api_type == api_type]