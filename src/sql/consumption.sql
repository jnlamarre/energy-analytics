CREATE TABLE consumption (
    id INTEGER,
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