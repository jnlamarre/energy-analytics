import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.config import load_config
from consumption.fetcher import fetch_consumption_data
from consumption.processor import save_consumption_data
from consumption.storage import load_consumption_to_database
from stations.fetcher import fetch_stations_data
from stations.processor import save_stations_data
from stations.storage import load_stations_to_database


def main():
    """Main entry point that processes all configured datasets."""
    print("Starting data pipeline processing...")
    
    # Load configuration
    configurations = load_config()
    
    for config in configurations:
        print(f"\nProcessing {config['nom_table']}...")
        
        try:
            # Fetch data based on API type
            if config["type_api"] == "economie_gouv":
                data = fetch_stations_data()
                save_stations_data(data)
                load_stations_to_database()
                
            elif config["type_api"] == "data_gouv":
                data = fetch_consumption_data()
                save_consumption_data(data)
                load_consumption_to_database()
                
            else:
                raise ValueError(f"Unknown API type: {config['type_api']}")
                
            print(f"✅ Successfully processed {config['nom_table']}")
            
        except Exception as e:
            print(f"❌ Error processing {config['nom_table']}: {e}")


if __name__ == "__main__":
    main()