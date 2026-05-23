from typing import List, Dict, Union
from datetime import datetime, timedelta
try:
    from ..utils.api_client import fetch_with_pagination
    from ..utils.config import get_config_by_table, build_api_url
except ImportError:
    from utils.api_client import fetch_with_pagination
    from utils.config import get_config_by_table, build_api_url


def fetch_consumption_data(start_date: str = None, end_date: str = None, single_date: str = None) -> List[Dict]:
    """
    Fetch energy consumption data from French government API.
    
    Args:
        start_date: Start date for range (YYYY-MM-DD format)
        end_date: End date for range (YYYY-MM-DD format)
        single_date: Single specific date (YYYY-MM-DD format)
                    If provided, overrides start_date and end_date
        
        If no parameters provided, fetches data for Jan 1 to March 31, 2026
    
    Returns:
        List of consumption records
    """
    print("Fetching consumption data...")
    
    # Get configuration
    config = get_config_by_table('consumption')
    if not config:
        raise ValueError("No configuration found for consumption table")
    
    # Build API URL from config
    base_url = build_api_url(config)
    
    # Determine query parameters
    if single_date:
        # Single date query
        params = {'Date__exact': f'"{single_date}"'}
        print(f"Fetching data for single date: {single_date}")
    else:
        # Date range query
        if not start_date:
            start_date = "2026-01-01"
        if not end_date:
            end_date = "2026-03-31"
            
        params = {
            'Date__greater': start_date,
            'Date__less': end_date
        }
        print(f"Fetching data for date range: {start_date} to {end_date}")
    
    try:
        data = fetch_with_pagination(base_url, params)
        print(f"Total consumption records collected: {len(data)}")
        return data
        
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []


def fetch_consumption_data_single_date(date: str = "2026-03-31") -> List[Dict]:
    """
    Legacy function for single date fetching (backwards compatibility).
    """
    return fetch_consumption_data(single_date=date)