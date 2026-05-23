import duckdb


def get_connection(db_path: str = '../data/energy-analytics.db') -> duckdb.DuckDBPyConnection:
    """Get a DuckDB connection to the analytics database."""
    return duckdb.connect(db_path)


def execute_query(query: str, db_path: str = '../data/energy-analytics.db'):
    """Execute a query and return results."""
    conn = get_connection(db_path)
    try:
        result = conn.execute(query).fetchall()
        return result
    finally:
        conn.close()


def execute_with_connection(func, db_path: str = '../data/energy-analytics.db'):
    """Execute a function with a database connection, ensuring proper cleanup."""
    conn = get_connection(db_path)
    try:
        return func(conn)
    finally:
        conn.close()