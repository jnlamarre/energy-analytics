import duckdb

# Connect to the database
conn = duckdb.connect('data/energy-analytics.db')

# Show all tables
print("=== AVAILABLE TABLES ===")
tables = conn.execute("SHOW TABLES").fetchall()
for table in tables:
    print(f"- {table[0]}")

print("\n" + "="*50)
print("CONSUMPTION DATA ANALYSIS")
print("="*50)

# Show consumption table info
print("\n=== CONSUMPTION TABLE SCHEMA ===")
result = conn.execute("DESCRIBE consumption").fetchall()
for row in result:
    print(f"{row[0]:<25} {row[1]:<15} {row[2]}")

print("\n=== CONSUMPTION RECORDS COUNT ===")
count = conn.execute("SELECT COUNT(*) FROM consumption").fetchone()
print(f"Total records: {count[0]}")

print("\n=== CONSUMPTION SAMPLE DATA ===")
sample = conn.execute("SELECT * FROM consumption LIMIT 3").fetchall()
for row in sample:
    print(row)

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

print("\n" + "="*50)
print("STATIONS DATA ANALYSIS") 
print("="*50)

# Show stations table info
print("\n=== STATIONS TABLE SCHEMA ===")
result = conn.execute("DESCRIBE stations").fetchall()
for row in result:
    print(f"{row[0]:<20} {row[1]:<15} {row[2]}")

print("\n=== STATIONS RECORDS COUNT ===")
count = conn.execute("SELECT COUNT(*) FROM stations").fetchone()
print(f"Total stations: {count[0]}")

print("\n=== STATIONS SAMPLE DATA ===")
sample = conn.execute("""
    SELECT id, city, gazole_price, sp95_price, latitude, longitude 
    FROM stations 
    WHERE gazole_price IS NOT NULL 
    LIMIT 3
""").fetchall()
for row in sample:
    print(f"Station {row[0]} in {row[1]}: Diesel €{row[2]}, SP95 €{row[3]} at ({row[4]:.3f}, {row[5]:.3f})")

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

conn.close()