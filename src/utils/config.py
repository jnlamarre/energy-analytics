from typing import Optional
from .configuration_classes import BaseConfiguration, ConfigurationManager


# Modern OOP interface
def get_configuration_by_table(table_name: str) -> Optional[BaseConfiguration]:
    """
    Get configuration object for a specific table.
    
    Args:
        table_name: Name of the table to get config for
        
    Returns:
        Configuration object or None if not found
    """
    return ConfigurationManager.get_configuration_by_table(table_name)


def get_all_configurations() -> list[BaseConfiguration]:
    """
    Get all configuration objects.
    
    Returns:
        List of configuration objects
    """
    return ConfigurationManager.load_all_configurations()