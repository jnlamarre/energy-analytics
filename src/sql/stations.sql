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