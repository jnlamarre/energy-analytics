from ..utils.database import get_connection


def show_consumption_stats(db_path: str = '../data/energy-analytics.db') -> None:
    """Display comprehensive consumption data statistics."""
    conn = get_connection(db_path)
    
    try:
        print("\n" + "="*50)
        print("CONSUMPTION DATA ANALYSIS")
        print("="*50)
        
        # Table schema
        print("\n=== CONSUMPTION TABLE SCHEMA ===")
        result = conn.execute("DESCRIBE consumption").fetchall()
        for row in result:
            print(f"{row[0]:<25} {row[1]:<15} {row[2]}")
        
        # Record count
        print("\n=== CONSUMPTION RECORDS COUNT ===")
        count = conn.execute("SELECT COUNT(*) FROM consumption").fetchone()
        print(f"Total records: {count[0]}")
        
        # Sample data
        print("\n=== CONSUMPTION SAMPLE DATA ===")
        sample = conn.execute("SELECT * FROM consumption LIMIT 3").fetchall()
        for row in sample:
            print(row)
        
        # Electricity consumption statistics
        print("\n=== ELECTRICITY CONSUMPTION STATS ===")
        stats = conn.execute("""
            SELECT 
                MIN(electricity_consumption_mw) as min_elec,
                MAX(electricity_consumption_mw) as max_elec,
                AVG(electricity_consumption_mw) as avg_elec,
                COUNT(*) as total_records
            FROM consumption 
            WHERE electricity_consumption_mw IS NOT NULL
        """).fetchone()
        print(f"Min: {stats[0]} MW")
        print(f"Max: {stats[1]} MW") 
        print(f"Avg: {stats[2]:.0f} MW")
        print(f"Records with data: {stats[3]}")
        
    finally:
        conn.close()