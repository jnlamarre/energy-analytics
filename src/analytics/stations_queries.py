try:
    from ..utils.database import get_connection
except ImportError:
    from utils.database import get_connection


def show_stations_stats(db_path: str = '../data/energy-analytics.db') -> None:
    """Display comprehensive stations data statistics."""
    conn = get_connection(db_path)
    
    try:
        print("\n" + "="*50)
        print("STATIONS DATA ANALYSIS") 
        print("="*50)
        
        # Table schema
        print("\n=== STATIONS TABLE SCHEMA ===")
        result = conn.execute("DESCRIBE stations").fetchall()
        for row in result:
            print(f"{row[0]:<20} {row[1]:<15} {row[2]}")
        
        # Record count
        print("\n=== STATIONS RECORDS COUNT ===")
        count = conn.execute("SELECT COUNT(*) FROM stations").fetchone()
        print(f"Total stations: {count[0]}")
        
        # Sample data
        print("\n=== STATIONS SAMPLE DATA ===")
        sample = conn.execute("""
            SELECT id, city, gazole_price, sp95_price, latitude, longitude 
            FROM stations 
            WHERE gazole_price IS NOT NULL 
            LIMIT 3
        """).fetchall()
        for row in sample:
            print(f"Station {row[0]} in {row[1]}: Diesel €{row[2]}, SP95 €{row[3]} at ({row[4]:.3f}, {row[5]:.3f})")
        
        # Fuel price statistics
        print("\n=== FUEL PRICE STATS ===")
        price_stats = conn.execute("""
            SELECT 
                COUNT(*) as total_stations,
                COUNT(gazole_price) as stations_with_diesel,
                COUNT(sp95_price) as stations_with_sp95,
                COUNT(sp98_price) as stations_with_sp98,
                MIN(gazole_price) as min_diesel,
                MAX(gazole_price) as max_diesel,
                AVG(gazole_price) as avg_diesel
            FROM stations
        """).fetchone()
        print(f"Total stations: {price_stats[0]}")
        print(f"Stations with diesel: {price_stats[1]}")
        print(f"Stations with SP95: {price_stats[2]}")
        print(f"Stations with SP98: {price_stats[3]}")
        print(f"Diesel price range: €{price_stats[4]} - €{price_stats[5]}")
        print(f"Average diesel price: €{price_stats[6]:.3f}")
        
        # Cheapest diesel stations
        print("\n=== TOP 5 CHEAPEST DIESEL STATIONS ===")
        cheap_diesel = conn.execute("""
            SELECT city, gazole_price, address
            FROM stations 
            WHERE gazole_price IS NOT NULL 
            ORDER BY gazole_price ASC 
            LIMIT 5
        """).fetchall()
        for row in cheap_diesel:
            print(f"{row[0]}: €{row[1]} - {row[2]}")
        
        # Regional statistics
        print("\n=== STATIONS BY REGION (TOP 10) ===")
        regions = conn.execute("""
            SELECT 
                SUBSTR(postal_code, 1, 2) as department,
                COUNT(*) as station_count,
                AVG(gazole_price) as avg_diesel_price
            FROM stations 
            WHERE postal_code IS NOT NULL AND gazole_price IS NOT NULL
            GROUP BY SUBSTR(postal_code, 1, 2)
            ORDER BY station_count DESC
            LIMIT 10
        """).fetchall()
        for row in regions:
            print(f"Dept {row[0]}: {row[1]} stations, avg diesel €{row[2]:.3f}")
            
    finally:
        conn.close()


def show_tables_overview(db_path: str = '../data/energy-analytics.db') -> None:
    """Display overview of all tables in the database."""
    conn = get_connection(db_path)
    
    try:
        print("=== AVAILABLE TABLES ===")
        tables = conn.execute("SHOW TABLES").fetchall()
        for table in tables:
            print(f"- {table[0]}")
            
    finally:
        conn.close()