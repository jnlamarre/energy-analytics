import duckdb

# Connect to the database
conn = duckdb.connect('energy-analytics.db')

# Show table info
print("=== TABLE SCHEMA ===")
result = conn.execute("DESCRIBE daily_gross_consumption").fetchall()
for row in result:
    print(row)

print("\n=== TOTAL RECORDS ===")
count = conn.execute("SELECT COUNT(*) FROM daily_gross_consumption").fetchone()
print(f"Total records: {count[0]}")

print("\n=== SAMPLE DATA ===")
sample = conn.execute("SELECT * FROM daily_gross_consumption LIMIT 5").fetchall()
for row in sample:
    print(row)

print("\n=== ELECTRICITY CONSUMPTION SUMMARY ===")
stats = conn.execute("""
    SELECT 
        MIN(electricity_consumption_mw) as min_elec,
        MAX(electricity_consumption_mw) as max_elec,
        AVG(electricity_consumption_mw) as avg_elec
    FROM daily_gross_consumption 
    WHERE electricity_consumption_mw IS NOT NULL
""").fetchone()
print(f"Min: {stats[0]}, Max: {stats[1]}, Avg: {stats[2]:.2f}")

conn.close()