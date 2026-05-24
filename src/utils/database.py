import duckdb
from typing import Optional


class DuckDBConnection:
    """Context manager for DuckDB connections with automatic cleanup."""
    
    def __init__(self, db_path: str = '../data/energy-analytics.db'):
        self.db_path = db_path
        self.connection: Optional[duckdb.DuckDBPyConnection] = None
    
    def __enter__(self) -> duckdb.DuckDBPyConnection:
        """Enter context manager - establish connection."""
        self.connection = duckdb.connect(self.db_path)
        return self.connection
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Exit context manager - cleanup connection."""
        if self.connection:
            self.connection.close()
        return False  # Don't suppress exceptions


def execute_query(query: str, db_path: str = '../data/energy-analytics.db'):
    """Execute a query using context manager pattern."""
    with DuckDBConnection(db_path) as conn:
        return conn.execute(query).fetchall()


def get_connection(db_path: str = '../data/energy-analytics.db') -> duckdb.DuckDBPyConnection:
    """
    Get a DuckDB connection to the analytics database.
    
    WARNING: This function is kept for backward compatibility only.
    Prefer using DuckDBConnection context manager for automatic cleanup.
    """
    return duckdb.connect(db_path)