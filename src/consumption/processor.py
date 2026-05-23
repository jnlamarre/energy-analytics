from typing import List, Dict
try:
    from ..utils.file_handler import save_json
    from ..utils.config import get_config_by_table
except ImportError:
    from utils.file_handler import save_json
    from utils.config import get_config_by_table


def save_consumption_data(data: List[Dict], file_path: str = None) -> None:
    """
    Save consumption data to JSON file.
    
    Args:
        data: List of consumption records
        file_path: Path where to save the file (uses config if None)
    """
    if file_path is None:
        config = get_config_by_table('consumption')
        if not config:
            raise ValueError("No configuration found for consumption table")
        file_path = config.get('fichier_cible')
        
    print("Saving consumption data to JSON file...")
    save_json(data, file_path)
    print(f"Data saved to {file_path}")