from typing import List, Dict, Optional
from .configuration_classes import BaseConfiguration, ConfigurationManager


# Legacy compatibility functions - use ConfigurationManager for new code
def load_config(config_file: str = 'config.json') -> List[Dict]:
    """
    Legacy function for backward compatibility.
    Use ConfigurationManager.load_all_configurations() for new code.
    """
    configurations = ConfigurationManager.load_all_configurations(config_file)
    return [config.config for config in configurations]


def get_config_by_table(table_name: str) -> Optional[Dict]:
    """
    Legacy function for backward compatibility.
    Use ConfigurationManager.get_configuration_by_table() for new code.
    """
    config = ConfigurationManager.get_configuration_by_table(table_name)
    return config.config if config else None



# Modern OOP interface - recommended for new code
def get_configuration_by_table(table_name: str) -> Optional[BaseConfiguration]:
    """
    Get configuration object for a specific table.
    
    Args:
        table_name: Name of the table to get config for
        
    Returns:
        Configuration object or None if not found
    """
    return ConfigurationManager.get_configuration_by_table(table_name)


def get_all_configurations() -> List[BaseConfiguration]:
    """
    Get all configuration objects.
    
    Returns:
        List of configuration objects
    """
    return ConfigurationManager.load_all_configurations()