import duckdb
from typing import List, Dict
try:
    from ..utils.database import get_connection
    from ..utils.file_handler import load_json
    from ..utils.config import get_config_by_table
    from .processor import process_station_coordinates
except ImportError:
    from utils.database import get_connection
    from utils.file_handler import load_json
    from utils.config import get_config_by_table
    from stations.processor import process_station_coordinates


def create_stations_table(conn: duckdb.DuckDBPyConnection) -> None:
    """Create the fuel stations table with proper schema."""
    conn.execute("DROP TABLE IF EXISTS stations")
    
    # Get SQL from config
    config = get_config_by_table('stations')
    if config and 'sql_creation' in config:
        conn.execute(config['sql_creation'])
    else:
        # Fallback to hardcoded SQL
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


def load_stations_to_database(db_path: str = '../data/energy-analytics.db') -> None:
    """
    Load fuel station data from JSON file into DuckDB database.
    
    Args:
        db_path: Path to the DuckDB database file
    """
    print("Loading stations data into database...")
    conn = get_connection(db_path)
    
    try:
        create_stations_table(conn)
        
        # Load data from JSON
        data = load_json('../data/stations.json')
        print(f"Processing {len(data)} stations...")
        
        # Insert data
        for station in data:
            try:
                lat, lon = process_station_coordinates(
                    station.get('latitude'), 
                    station.get('longitude')
                )
                
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
            
    finally:
        conn.close()
        
    print("Database loading completed!")