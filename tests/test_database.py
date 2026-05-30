import pytest
import tempfile
import os
from unittest.mock import Mock, patch

from utils.database import DuckDBConnection, execute_query, get_connection


class TestDuckDBConnection:
    
    def test_context_manager_successful_connection(self):
        # Use a unique temp file name that doesn't exist yet
        temp_dir = tempfile.gettempdir()
        temp_db_path = os.path.join(temp_dir, f"test_db_{os.getpid()}.db")
        
        try:
            with DuckDBConnection(temp_db_path) as conn:
                assert conn is not None
                # Test basic query to verify connection works
                result = conn.execute("SELECT 1 AS test").fetchall()
                assert result == [(1,)]
        finally:
            if os.path.exists(temp_db_path):
                os.unlink(temp_db_path)
    
    def test_context_manager_cleanup(self):
        # Use a unique temp file name that doesn't exist yet
        temp_dir = tempfile.gettempdir()
        temp_db_path = os.path.join(temp_dir, f"test_cleanup_{os.getpid()}.db")
        
        try:
            connection = None
            with DuckDBConnection(temp_db_path) as conn:
                connection = conn
                assert conn is not None
            
            # After exiting context, connection should be cleaned up
            # Note: DuckDB connections don't have an easy way to check if closed,
            # but we can verify the context manager completed
            assert connection is not None
        finally:
            if os.path.exists(temp_db_path):
                os.unlink(temp_db_path)
    
    def test_path_adjustment_from_root(self):
        # Mock os.path.exists to simulate running from project root
        with patch('os.path.exists') as mock_exists:
            mock_exists.side_effect = lambda path: path in ['data', 'config.json']
            
            connection_manager = DuckDBConnection('data/test.db')
            assert connection_manager.db_path == 'data/test.db'
    
    def test_path_adjustment_from_src(self):
        # Mock os.path.exists to simulate running from src directory
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = False
            
            connection_manager = DuckDBConnection('data/test.db')
            assert connection_manager.db_path == '../data/test.db'
    
    def test_path_adjustment_already_relative(self):
        # Mock os.path.exists to simulate running from src directory
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = False
            
            connection_manager = DuckDBConnection('../data/test.db')
            assert connection_manager.db_path == '../data/test.db'
    
    def test_exception_propagation(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as temp_db:
            temp_db_path = temp_db.name
        
        try:
            with pytest.raises(Exception):
                with DuckDBConnection(temp_db_path) as conn:
                    # Force an exception
                    raise Exception("Test exception")
        finally:
            if os.path.exists(temp_db_path):
                os.unlink(temp_db_path)


class TestExecuteQuery:
    
    def test_execute_query_successful(self):
        # Use a unique temp file name that doesn't exist yet
        temp_dir = tempfile.gettempdir()
        temp_db_path = os.path.join(temp_dir, f"test_execute_{os.getpid()}.db")
        
        try:
            result = execute_query("SELECT 42 AS answer", temp_db_path)
            assert result == [(42,)]
        finally:
            if os.path.exists(temp_db_path):
                os.unlink(temp_db_path)
    
    def test_execute_query_with_table_creation(self):
        # Use a unique temp file name that doesn't exist yet
        temp_dir = tempfile.gettempdir()
        temp_db_path = os.path.join(temp_dir, f"test_table_{os.getpid()}.db")
        
        try:
            # Create a table and insert data
            execute_query("CREATE TABLE test (id INTEGER, name TEXT)", temp_db_path)
            execute_query("INSERT INTO test VALUES (1, 'Alice'), (2, 'Bob')", temp_db_path)
            
            # Query the data
            result = execute_query("SELECT * FROM test ORDER BY id", temp_db_path)
            assert result == [(1, 'Alice'), (2, 'Bob')]
        finally:
            if os.path.exists(temp_db_path):
                os.unlink(temp_db_path)
    
    def test_execute_query_invalid_sql(self):
        # Use a unique temp file name that doesn't exist yet
        temp_dir = tempfile.gettempdir()
        temp_db_path = os.path.join(temp_dir, f"test_invalid_{os.getpid()}.db")
        
        try:
            with pytest.raises(Exception):
                execute_query("INVALID SQL STATEMENT", temp_db_path)
        finally:
            if os.path.exists(temp_db_path):
                os.unlink(temp_db_path)


class TestGetConnection:
    
    def test_get_connection_successful(self):
        # Use a unique temp file name that doesn't exist yet
        temp_dir = tempfile.gettempdir()
        temp_db_path = os.path.join(temp_dir, f"test_connection_{os.getpid()}.db")
        
        try:
            conn = get_connection(temp_db_path)
            assert conn is not None
            
            # Test the connection works
            result = conn.execute("SELECT 'test' AS message").fetchall()
            assert result == [('test',)]
            
            # Clean up manually since this function doesn't use context manager
            conn.close()
        finally:
            if os.path.exists(temp_db_path):
                os.unlink(temp_db_path)
    
    def test_get_connection_manual_cleanup_required(self):
        # This test demonstrates why the context manager is preferred
        # Use a unique temp file name that doesn't exist yet
        temp_dir = tempfile.gettempdir()
        temp_db_path = os.path.join(temp_dir, f"test_manual_{os.getpid()}.db")
        
        try:
            conn = get_connection(temp_db_path)
            assert conn is not None
            
            # User must remember to close manually
            conn.close()
        finally:
            if os.path.exists(temp_db_path):
                os.unlink(temp_db_path)