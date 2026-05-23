import duckdb
try:
    from ..utils.database import get_connection
    from ..utils.config import get_config_by_table
except ImportError:
    from utils.database import get_connection
    from utils.config import get_config_by_table


def create_consumption_table(conn: duckdb.DuckDBPyConnection) -> None:
    """Create the energy consumption table with proper schema."""
    conn.execute("DROP TABLE IF EXISTS consumption")
    
    # Get SQL from config
    config = get_config_by_table('consumption')
    if config and 'sql_creation' in config:
        conn.execute(config['sql_creation'])
    else:
        # Fallback to hardcoded SQL
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


def load_consumption_to_database(db_path: str = '../data/energy-analytics.db') -> None:
    """
    Load consumption data from JSON file into DuckDB database.
    
    Args:
        db_path: Path to the DuckDB database file
    """
    print("Loading consumption data into database...")
    conn = get_connection(db_path)
    
    try:
        create_consumption_table(conn)
        
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
            FROM read_json('../data/consumption.json')
        """)
        
        # Verify data was written
        result = conn.execute("SELECT COUNT(*) as count FROM consumption").fetchone()
        print(f"Records written to DuckDB: {result[0]}")
        
        # Show sample data
        sample = conn.execute("SELECT * FROM consumption LIMIT 3").fetchall()
        print("Sample data from DuckDB:")
        for row in sample:
            print(row)
            
    finally:
        conn.close()
        
    print("Database operation completed successfully!")