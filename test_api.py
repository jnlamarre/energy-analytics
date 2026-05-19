import requests
import duckdb
import json

print("Downloading data from API...")

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

print("Saving data to JSON file...")
# Save data to JSON file
with open('daily_raw_consumption.json', 'w', encoding='utf-8') as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)

print("Data saved to daily_raw_consumption.json")

print("Loading data into database...")
# Write data to DuckDB
conn = duckdb.connect('energy-analytics.db')

# Drop old table and create new one with consistent naming
conn.execute("DROP TABLE IF EXISTS daily_gross_consumption")

# Create table with English column names and proper schema
conn.execute("""
    CREATE TABLE daily_raw_consumption (
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

# Insert data from JSON
conn.execute("""
    INSERT INTO daily_raw_consumption
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
    FROM read_json('daily_raw_consumption.json')
""")

# Verify data was written
result = conn.execute("SELECT COUNT(*) as count FROM daily_raw_consumption").fetchone()
print(f"Records written to DuckDB: {result[0]}")

# Show sample data
sample = conn.execute("SELECT * FROM daily_raw_consumption LIMIT 3").fetchall()
print(f"\nSample data from DuckDB:")
for row in sample:
    print(row)

print("Database operation completed successfully!")
conn.close()