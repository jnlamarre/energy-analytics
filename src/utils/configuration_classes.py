from typing import Optional
import json
import os
from pydantic.dataclasses import dataclass


@dataclass
class DataGouvConfiguration:
    """
    Configuration for data.gouv.fr Tabular API (energy consumption data).
    """
    api_type: str
    dataset: str
    target_file: str
    sql_file: str
    sql_creation: str
    table_name: str

    @property
    def url(self) -> str:
        """
        Build Tabular API URL dynamically.
        
        Returns:
            Complete API URL for data.gouv.fr tabular API
        """
        return f'https://tabular-api.data.gouv.fr/api/resources/{self.dataset}/data/'
    
    @property
    def target_file_path(self) -> str:
        """
        Get the target file path adjusted for current working directory.
        
        Returns:
            Adjusted target file path
        """
        if os.path.exists('data') and os.path.exists('config.json'):
            # Running from project root (has both data and config.json)
            return self.target_file.replace('../', '')
        else:
            # Running from src/ directory
            return self.target_file


@dataclass
class EconomieGouvConfiguration:
    """
    Configuration for data.economie.gouv.fr OpenData API (fuel station data).
    """
    api_type: str
    dataset: str
    target_file: str
    sql_file: str
    sql_creation: str
    table_name: str
    select: Optional[list[str]] = None

    @property
    def url(self) -> str:
        """
        Build OpenData API URL template with select parameters.
        
        Returns:
            API URL template with {step} and {offset} placeholders
        """
        base_url = f'https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/{self.dataset}/records'
        
        if self.select:
            select_param = "%2C".join(self.select)
            return f"{base_url}?select={select_param}&limit={{step}}&offset={{offset}}"
        else:
            return f"{base_url}?limit={{step}}&offset={{offset}}"
    
    @property
    def target_file_path(self) -> str:
        """
        Get the target file path adjusted for current working directory.
        
        Returns:
            Adjusted target file path
        """
        if os.path.exists('data') and os.path.exists('config.json'):
            # Running from project root (has both data and config.json)
            return self.target_file.replace('../', '')
        else:
            # Running from src/ directory
            return self.target_file


# Type alias for configuration objects (Python 3.10+ syntax)
BaseConfiguration = DataGouvConfiguration | EconomieGouvConfiguration


class ConfigurationManager:
    """
    Manager class for loading and managing Pydantic dataclass configurations.
    """
    
    @classmethod
    def load_all_configurations(cls, config_file: str = 'config.json') -> list[BaseConfiguration]:
        """
        Load all configurations from JSON file into Pydantic dataclass objects.
        
        Args:
            config_file: Name of the configuration file
            
        Returns:
            List of configuration dataclass objects
        """
        config_path = os.path.join(os.path.dirname(__file__), '..', '..', config_file)
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config_dicts = json.load(f)
        
        configurations = []
        for config_dict in config_dicts:
            # Load SQL content
            if 'sql_file' in config_dict:
                config_dict['sql_creation'] = cls._load_sql_file(config_dict['sql_file'])
            
            # Create appropriate configuration object using **kwargs unpacking
            api_type = config_dict.get('api_type')
            if api_type == 'data_gouv':
                configurations.append(DataGouvConfiguration(**config_dict))
            elif api_type == 'economie_gouv':
                configurations.append(EconomieGouvConfiguration(**config_dict))
            else:
                raise ValueError(f"Unsupported API type: {api_type}")
        
        return configurations
    
    @classmethod
    def get_configuration_by_table(cls, table_name: str) -> Optional[BaseConfiguration]:
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
    def get_configurations_by_api_type(cls, api_type: str) -> list[BaseConfiguration]:
        """
        Get all configurations for a specific API type.
        
        Args:
            api_type: Type of API ('data_gouv' or 'economie_gouv')
            
        Returns:
            List of configuration objects for the specified API type
        """
        configurations = cls.load_all_configurations()
        
        return [config for config in configurations if config.api_type == api_type]
    
    @classmethod
    def _load_sql_file(cls, sql_filename: str) -> str:
        """
        Load SQL content from file.
        
        Args:
            sql_filename: Name of the SQL file
            
        Returns:
            SQL content as string
        """
        sql_path = os.path.join(os.path.dirname(__file__), '..', '..', 'sql', sql_filename)
        with open(sql_path, 'r', encoding='utf-8') as f:
            return f.read()