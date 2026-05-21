import requests
import duckdb
import json

def fetch_data():
    """Fetch fuel station data from French government API"""
    url = 'https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/prix-des-carburants-en-france-flux-instantane-v2/records?select=id%2Clatitude%2Clongitude%2Ccp%2Cadresse%2Cville%2Cservices%2Cgazole_prix%2Cgazole_maj%2Choraires%2Csp95_maj%2Csp95_prix%2Csp98_maj%2Csp98_prix&limit={limit}&offset={offset}'
    
    all_data = []
    total_count = 1
    limit = 100
    offset = 0
    
    print("Fetching station data...")
    
    while True:
        try:
            response = requests.get(url.format(limit=limit, offset=offset))
            response.raise_for_status()
            data = response.json()
            
            results = data.get('results', [])
            if not results:
                break
                
            all_data.extend(results)
            total_count = data.get('total_count', 0)
            
            print(f"Fetched {len(results)} stations (offset {offset}). Total: {len(all_data)}/{total_count}")
            
            # Check if we have all data
            if len(all_data) >= total_count:
                break
                
            offset += limit
                
        except requests.RequestException as e:
            print(f"Error fetching data: {e}")
            break
    
    print(f"Total stations fetched: {len(all_data)}")
    return all_data

def save_to_json(data):
    """Save fuel data to JSON file"""
    with open('data/stations.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Data saved to stations.json")

def create_fuel_stations_table(conn):
    """Create the fuel stations table with proper schema"""
    
    conn.execute("""
        DROP TABLE IF EXISTS stations
    """)
    
    conn.execute("""
        CREATE TABLE stations (
            id BIGINT PRIMARY KEY,
            latitude DOUBLE,
            longitude DOUBLE,
            postal_code VARCHAR(10),
            address VARCHAR(200),
            city VARCHAR(100),
            services_json TEXT,
            hours_json TEXT,
            
            -- Diesel (Gazole)
            gazole_price DECIMAL(5,3),
            gazole_updated TIMESTAMPTZ,
            
            -- SP95
            sp95_price DECIMAL(5,3),
            sp95_updated TIMESTAMPTZ,
            
            -- SP98
            sp98_price DECIMAL(5,3),
            sp98_updated TIMESTAMPTZ
        )
    """)

def load_to_database():
    """Load fuel station data into DuckDB"""
    print("Loading data into database...")
    
    conn = duckdb.connect('data/energy-analytics.db')
    
    # Create table
    create_fuel_stations_table(conn)
    
    # Read data from JSON
    with open('data/stations.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Processing {len(data)} stations...")
    
    # Insert data
    for station in data:
        try:
            # Convert coordinates from strings to floats
            lat = float(station.get('latitude', 0)) / 100000 if station.get('latitude') else None
            lon = float(station.get('longitude', 0)) / 100000 if station.get('longitude') else None
            
            conn.execute("""
                INSERT INTO stations (
                    id, latitude, longitude, postal_code, address, city,
                    services_json, hours_json,
                    gazole_price, gazole_updated,
                    sp95_price, sp95_updated,
                    sp98_price, sp98_updated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                station.get('id'),
                lat,
                lon,
                station.get('cp'),
                station.get('adresse'),
                station.get('ville'),
                station.get('services'),
                station.get('horaires'),
                station.get('gazole_prix'),
                station.get('gazole_maj'),
                station.get('sp95_prix'),
                station.get('sp95_maj'),
                station.get('sp98_prix'),
                station.get('sp98_maj')
            ])
            
        except Exception as e:
            print(f"Error inserting station {station.get('id')}: {e}")
            continue
    
    # Verify data
    count = conn.execute("SELECT COUNT(*) FROM stations").fetchone()[0]
    print(f"Successfully loaded {count} stations")
    
    # Show sample data
    print("\nSample data:")
    sample = conn.execute("""
        SELECT id, city, gazole_price, sp95_price, latitude, longitude 
        FROM stations 
        WHERE gazole_price IS NOT NULL 
        LIMIT 3
    """).fetchall()
    
    for row in sample:
        print(f"Station {row[0]} in {row[1]}: Diesel €{row[2]}, SP95 €{row[3]} at ({row[4]:.3f}, {row[5]:.3f})")
    
    conn.close()
    print("Database loading completed!")

def main():
    """Main pipeline for fuel prices data"""
    try:
        # Fetch data from API
        data = fetch_data()
        
        # Save to JSON
        save_to_json(data)
        
        # Load to database
        load_to_database()
        
        print("\nStations pipeline completed successfully!")
        
    except Exception as e:
        print(f"Error in pipeline: {e}")

if __name__ == "__main__":
    main()