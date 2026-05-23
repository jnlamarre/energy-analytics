import sys
sys.path.append('..')

from src.stations.fetcher import fetch_stations_data
from src.stations.processor import save_stations_data
from src.stations.storage import load_stations_to_database


def main():
    """Main pipeline for fuel prices data"""
    try:
        # Fetch data from API
        data = fetch_stations_data()
        
        # Save to JSON
        save_stations_data(data)
        
        # Load to database
        load_stations_to_database()
        
        print("\nStations pipeline completed successfully!")
        
    except Exception as e:
        print(f"Error in pipeline: {e}")


if __name__ == "__main__":
    main()