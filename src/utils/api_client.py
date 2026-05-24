import requests
from typing import Any, Optional


def fetch_with_pagination(
    base_url: str,
    params: dict[str, Any] | None = None,
    pagination_key: str = 'next',
    data_key: str = 'data'
) -> list[dict]:
    """
    Fetch data from an API with pagination support.
    
    Args:
        base_url: The base URL for the API
        params: Additional query parameters
        pagination_key: Key in response that contains next page URL
        data_key: Key in response that contains the data array
    
    Returns:
        List of all fetched records
    """
    all_data = []
    url = base_url
    
    while url:
        try:
            response = requests.get(url, params=params if url == base_url else None)
            response.raise_for_status()
            data = response.json()
            
            # Extract data records
            records = data.get(data_key, [])
            if not records:
                break
                
            all_data.extend(records)
            
            # Get next page URL
            if 'links' in data and pagination_key in data['links']:
                url = data['links'][pagination_key]
            else:
                url = None
                
        except requests.RequestException as e:
            print(f"Error fetching data: {e}")
            break
    
    return all_data


def fetch_paginated_api(
    url_template: str,
    limit: int = 100,
    max_records: Optional[int] = None
) -> list[dict]:
    """
    Fetch data from an API using offset-based pagination.
    
    Args:
        url_template: URL template with {limit} and {offset} placeholders
        limit: Number of records per page
        max_records: Maximum total records to fetch (None for all)
    
    Returns:
        List of all fetched records
    """
    all_data = []
    offset = 0
    
    while True:
        try:
            url = url_template.format(limit=limit, offset=offset)
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            results = data.get('results', [])
            if not results:
                break
                
            all_data.extend(results)
            
            # Check if we've reached the total or max limit
            total_count = data.get('total_count', 0)
            if len(all_data) >= total_count or (max_records and len(all_data) >= max_records):
                break
                
            offset += limit
                
        except requests.RequestException as e:
            print(f"Error fetching data at offset {offset}: {e}")
            break
    
    return all_data