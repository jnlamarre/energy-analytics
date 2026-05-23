import sys
sys.path.append('..')

from src.consumption.fetcher import fetch_consumption_data
from src.consumption.processor import save_consumption_data
from src.consumption.storage import load_consumption_to_database


def main():
    """Main pipeline for energy consumption data"""
    try:
        # Fetch data from API
        data = fetch_consumption_data()
        
        # Save to JSON
        save_consumption_data(data)
        
        # Load to database
        load_consumption_to_database()
        
        print("\nConsumption pipeline completed successfully!")
        
    except Exception as e:
        print(f"Error in pipeline: {e}")


if __name__ == "__main__":
    main()