import requests
import duckdb
import json

def fetch_data():
    """Fetch energy consumption data from French government API"""
    print("Fetching consumption data...")

    all_data = []
    url = 'https://tabular-api.data.gouv.fr/api/resources/cfc27ff9-1871-4ee8-be64-b9a290c06935/data/?Date__exact="2026-03-31"'

    while url:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        all_data.extend(data['data'])
        
        # Get next page URL using safer .get() method
        url = data['links'].get('next')
        
        print(f"Fetched page with {len(data['data'])} records. Total so far: {len(all_data)}")

    print(f"\nTotal records collected: {len(all_data)}")
    
    return all_data

def save_to_json(data):
    """Save data to JSON file"""
    print("Saving data to JSON file...")
    with open('data/consumption.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Data saved to consumption.json")

def create_database_table(conn):
    """Create the energy consumption table"""
    # Drop old table and create new one
    conn.execute("DROP TABLE IF EXISTS consumption")
    
    # Create table with English column names and proper schema
    conn.execute("""
        CREATE TABLE consumption (
            date DATE,
            time_slot STRING,
            flag_ignore BOOLEAN,
            datetime_str STRING,
            electricity_status STRING,
            gas_natran_status STRING,
            gas_terega_status STRING,
            total_consumption_mw INTEGER,
            total_gas_consumption_mw INTEGER,
            electricity_consumption_mw INTEGER,
            gas_natran_consumption_mw INTEGER,
            gas_terega_consumption_mw INTEGER
        )
    """)

def load_to_database():
    """Load data into DuckDB database"""
    print("Loading data into database...")
    conn = duckdb.connect('data/energy-analytics.db')
    
    create_database_table(conn)
    
    # Insert data from JSON
    conn.execute("""
        INSERT INTO consumption
        SELECT 
            CAST(Date AS DATE) as date,
            Heure::STRING as time_slot,
            flag_ignore::BOOLEAN as flag_ignore,
            "Date - Heure"::STRING as datetime_str,
            "Statut - RTE"::STRING as electricity_status,
            "Statut - NaTran"::STRING as gas_natran_status,
            "Statut - Teréga"::STRING as gas_terega_status,
            "Consommation brute totale (MW)"::INTEGER as total_consumption_mw,
            "Consommation brute gaz totale (MW PCS 0°C)"::INTEGER as total_gas_consumption_mw,
            "Consommation brute électricité (MW) - RTE"::INTEGER as electricity_consumption_mw,
            "Consommation brute gaz (MW PCS 0°C) - NaTran"::INTEGER as gas_natran_consumption_mw,
            "Consommation brute gaz (MW PCS 0°C) - Teréga"::INTEGER as gas_terega_consumption_mw
        FROM read_json('data/consumption.json')
    """)
    
    # Verify data was written
    result = conn.execute("SELECT COUNT(*) as count FROM consumption").fetchone()
    print(f"Records written to DuckDB: {result[0]}")
    
    # Show sample data
    sample = conn.execute("SELECT * FROM consumption LIMIT 3").fetchall()
    print(f"\nSample data from DuckDB:")
    for row in sample:
        print(row)
    
    conn.close()
    print("Database operation completed successfully!")

def main():
    """Main pipeline for energy consumption data"""
    try:
        # Fetch data from API
        data = fetch_data()
        
        # Save to JSON
        save_to_json(data)
        
        # Load to database
        load_to_database()
        
        print("\nConsumption pipeline completed successfully!")
        
    except Exception as e:
        print(f"Error in pipeline: {e}")

if __name__ == "__main__":
    main()