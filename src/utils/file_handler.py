import json
from typing import Any


def save_json(data: Any, file_path: str, encoding: str = 'utf-8') -> None:
    """
    Save data to a JSON file.
    
    Args:
        data: Data to save (list, dict, etc.)
        file_path: Path where to save the file
        encoding: File encoding (default: utf-8)
    """
    with open(file_path, 'w', encoding=encoding) as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_json(file_path: str, encoding: str = 'utf-8') -> Any:
    """
    Load data from a JSON file.
    
    Args:
        file_path: Path to the JSON file
        encoding: File encoding (default: utf-8)
    
    Returns:
        Loaded data
    """
    with open(file_path, 'r', encoding=encoding) as f:
        return json.load(f)