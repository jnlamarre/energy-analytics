from typing import List, Dict, Optional, Tuple
try:
    from ..utils.file_handler import save_json
    from ..utils.config import get_config_by_table
except ImportError:
    from utils.file_handler import save_json
    from utils.config import get_config_by_table


def process_station_coordinates(latitude: str, longitude: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Convert coordinate strings to float values with proper scaling.
    
    Args:
        latitude: Latitude as string
        longitude: Longitude as string
    
    Returns:
        Tuple of (lat, lon) as floats, or (None, None) if conversion fails
    """
    try:
        lat = float(latitude) / 100000 if latitude else None
        lon = float(longitude) / 100000 if longitude else None
        return lat, lon
    except (ValueError, TypeError):
        return None, None


def save_stations_data(data: List[Dict], file_path: str = None) -> None:
    """
    Save stations data to JSON file.
    
    Args:
        data: List of station records
        file_path: Path where to save the file (uses config if None)
    """
    if file_path is None:
        config = get_config_by_table('stations')
        if not config:
            raise ValueError("No configuration found for stations table")
        file_path = config.get('fichier_cible')
        
    print("Saving stations data to JSON file...")
    save_json(data, file_path)
    print(f"Data saved to {file_path}")