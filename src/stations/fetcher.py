from typing import List, Dict
try:
    from ..utils.api_client import fetch_paginated_api
    from ..utils.config import get_config_by_table, build_api_url
except ImportError:
    from utils.api_client import fetch_paginated_api
    from utils.config import get_config_by_table, build_api_url


def fetch_stations_data() -> List[Dict]:
    """
    Fetch fuel station data from French government API.
    
    Returns:
        List of fuel station records
    """
    print("Fetching station data...")
    
    # Get configuration
    config = get_config_by_table('stations')
    if not config:
        raise ValueError("No configuration found for stations table")
    
    # Build URL template from config
    url_template = build_api_url(config, limit='{limit}', offset='{offset}')
    
    data = fetch_paginated_api(url_template)
    print(f"Total stations fetched: {len(data)}")
    
    return data