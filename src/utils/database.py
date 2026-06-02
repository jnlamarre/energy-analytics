import os
from typing import Optional

import duckdb


class DuckDBConnection:
    """Context manager for DuckDB connections with automatic cleanup."""

    def __init__(self, db_path: str = "data/energy-analytics.db"):
        # Auto-detect correct path based on working directory
        if os.path.isabs(db_path):
            # Absolute path - use as-is
            self.db_path = db_path
        elif os.path.exists("data") and os.path.exists("config.json"):
            # Running from project root (has both data and config.json)
            self.db_path = (
                db_path if not db_path.startswith("../") else db_path.replace("../", "")
            )
        else:
            # Running from src/ directory
            self.db_path = f"../{db_path}" if not db_path.startswith("../") else db_path
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


def execute_query(query: str, db_path: str = "data/energy-analytics.db") -> list:
    """Execute a query using context manager pattern."""
    with DuckDBConnection(db_path) as conn:
        return conn.execute(query).fetchall()


def get_connection(
    db_path: str = "data/energy-analytics.db",
) -> duckdb.DuckDBPyConnection:
    """
    Get a DuckDB connection to the analytics database.

    WARNING: This function is kept for backward compatibility only.
    Prefer using DuckDBConnection context manager for automatic cleanup.
    """
    return duckdb.connect(db_path)
