import json
import os
from typing import List, Dict, Optional


def load_sql_file(sql_filename: str) -> str:
    """
    Load SQL content from file.
    
    Args:
        sql_filename: Name of the SQL file
        
    Returns:
        SQL content as string
    """
    sql_path = os.path.join(os.path.dirname(__file__), '..', 'sql', sql_filename)
    with open(sql_path, 'r', encoding='utf-8') as f:
        return f.read()


def load_config(config_file: str = 'config.json') -> List[Dict]:
    """
    Load configuration from JSON file and populate SQL creation statements.
    
    Args:
        config_file: Name of the configuration file (in utils directory)
        
    Returns:
        List of configuration dictionaries with SQL content loaded
    """
    config_path = os.path.join(os.path.dirname(__file__), config_file)
    
    with open(config_path, 'r', encoding='utf-8') as f:
        configs = json.load(f)
    
    # Load SQL content for each config
    for config in configs:
        if 'fichier_sql' in config:
            config['sql_creation'] = load_sql_file(config['fichier_sql'])
    
    return configs


def get_config_by_table(table_name: str) -> Optional[Dict]:
    """
    Get configuration for a specific table.
    
    Args:
        table_name: Name of the table to get config for
        
    Returns:
        Configuration dictionary or None if not found
    """
    configs = load_config()
    for config in configs:
        if config.get('nom_table') == table_name:
            return config
    return None


def get_config_by_dataset(dataset_id: str) -> Optional[Dict]:
    """
    Get configuration for a specific dataset.
    
    Args:
        dataset_id: Dataset identifier
        
    Returns:
        Configuration dictionary or None if not found
    """
    configs = load_config()
    for config in configs:
        if config.get('dataset') == dataset_id:
            return config
    return None


def get_api_configs() -> Dict[str, List[Dict]]:
    """
    Get configurations grouped by API type.
    
    Returns:
        Dictionary with API types as keys and list of configs as values
    """
    configs = load_config()
    api_configs = {}
    
    for config in configs:
        api_type = config.get('type_api')
        if api_type not in api_configs:
            api_configs[api_type] = []
        api_configs[api_type].append(config)
    
    return api_configs


# API URL builders based on config
def build_api_url(config: Dict, **kwargs) -> str:
    """
    Build API URL based on configuration and parameters.
    
    Args:
        config: Configuration dictionary
        **kwargs: Additional parameters for URL building
        
    Returns:
        Complete API URL
    """
    api_type = config.get('type_api')
    dataset = config.get('dataset')
    
    if api_type == 'data_gouv':
        # Tabular API format
        base_url = f'https://tabular-api.data.gouv.fr/api/resources/{dataset}/data/'
        return base_url
        
    elif api_type == 'economie_gouv':
        # OpenData API format with pagination
        base_url = f'https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/{dataset}/records'
        
        # Add select parameters for fuel station data
        if 'prix-des-carburants' in dataset:
            select_params = 'id%2Clatitude%2Clongitude%2Ccp%2Cadresse%2Cville%2Cservices%2Cgazole_prix%2Cgazole_maj%2Choraires%2Csp95_maj%2Csp95_prix%2Csp98_maj%2Csp98_prix'
            base_url += f'?select={select_params}'
            
            # Add pagination parameters
            limit = kwargs.get('limit', 100)
            offset = kwargs.get('offset', 0)
            base_url += f'&limit={limit}&offset={offset}'
        
        return base_url
    
    else:
        raise ValueError(f"Unsupported API type: {api_type}")