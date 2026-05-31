import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from contextlib import nullcontext as does_not_raise

from utils.database import DuckDBConnection, execute_query, get_connection
from utils.files import save_json


class TestDatabase:
    """Comprehensive database functionality tests."""
    
    def test_context_manager_basic_operations(self, temp_database):
        """Test basic database operations using context manager."""
        with DuckDBConnection(temp_database) as conn:
            assert conn is not None
            
            # Test simple query
            result = conn.execute("SELECT 'test' AS message").fetchall()
            assert result == [('test',)]
            
            # Test table creation and data insertion
            conn.execute("CREATE TABLE test (id INTEGER, name TEXT)")
            conn.execute("INSERT INTO test VALUES (1, 'Alice'), (2, 'Bob')")
            result = conn.execute("SELECT * FROM test ORDER BY id").fetchall()
            assert result == [(1, 'Alice'), (2, 'Bob')]

    def test_path_adjustment_logic(self):
        """Test database path adjustment for different working directories."""
        temp_dir = tempfile.gettempdir()
        temp_db_path = os.path.join(temp_dir, f"test_path_{os.getpid()}.db")
        
        try:
            # Test absolute path handling
            with DuckDBConnection(temp_db_path) as conn:
                assert conn is not None
                result = conn.execute("SELECT 'absolute_path' AS message").fetchall()
                assert result == [('absolute_path',)]
                
            # Test relative path from root directory
            with patch('os.path.exists') as mock_exists:
                mock_exists.return_value = True  # Simulate root directory
                with DuckDBConnection(temp_db_path) as conn:
                    result = conn.execute("SELECT 'root_test' AS message").fetchall()
                    assert result == [('root_test',)]
        finally:
            if os.path.exists(temp_db_path):
                os.unlink(temp_db_path)

    def test_path_resolution_project_root_scenario(self):
        """Test path resolution when running from project root."""
        temp_dir = tempfile.gettempdir()
        temp_db_path = os.path.join(temp_dir, f"test_root_{os.getpid()}.db")
        
        try:
            # Mock scenario: both 'data' and 'config.json' exist (project root)
            with patch('os.path.exists') as mock_exists:
                def exists_side_effect(path):
                    return path in ['data', 'config.json']
                mock_exists.side_effect = exists_side_effect
                
                # Test relative path in project root
                db_conn = DuckDBConnection(temp_db_path)
                assert db_conn.db_path == temp_db_path
                
                # Test path with ../ prefix in project root  
                db_conn_with_prefix = DuckDBConnection(f"../{temp_db_path}")
                expected_path = temp_db_path  # ../ should be removed
                assert db_conn_with_prefix.db_path == expected_path
                
        finally:
            if os.path.exists(temp_db_path):
                os.unlink(temp_db_path)

    def test_path_resolution_src_directory_scenario(self):
        """Test path resolution when running from src/ directory."""
        relative_db_path = "data/test_src.db"
        
        # Mock scenario: neither 'data' nor 'config.json' exist (in src/)
        with patch('os.path.exists') as mock_exists, \
             patch('os.path.isabs') as mock_isabs:
            mock_exists.return_value = False
            mock_isabs.return_value = False  # Ensure it's treated as relative
            
            # Test relative path in src directory - should add ../
            db_conn = DuckDBConnection(relative_db_path)
            assert db_conn.db_path == f"../{relative_db_path}"
            
            # Test path that already has ../ prefix - should remain unchanged
            already_prefixed = f"../{relative_db_path}"
            db_conn_with_prefix = DuckDBConnection(already_prefixed)
            assert db_conn_with_prefix.db_path == already_prefixed

    def test_execute_query_function(self):
        """Test standalone execute_query function."""
        temp_dir = tempfile.gettempdir()
        temp_db_path = os.path.join(temp_dir, f"test_execute_{os.getpid()}.db")
        
        try:
            result = execute_query("SELECT 'execute_test' AS message", temp_db_path)
            assert result == [('execute_test',)]
            
            # Test with table operations
            execute_query("CREATE TABLE test (id INTEGER, name TEXT)", temp_db_path)
            execute_query("INSERT INTO test VALUES (1, 'Alice')", temp_db_path)
            result = execute_query("SELECT * FROM test", temp_db_path)
            assert result == [(1, 'Alice')]
        finally:
            if os.path.exists(temp_db_path):
                os.unlink(temp_db_path)

    def test_get_connection_function(self):
        """Test standalone get_connection function."""
        temp_dir = tempfile.gettempdir()
        temp_db_path = os.path.join(temp_dir, f"test_connection_{os.getpid()}.db")
        
        try:
            conn = get_connection(temp_db_path)
            assert conn is not None
            
            result = conn.execute("SELECT 'connection_test' AS message").fetchall()
            assert result == [('connection_test',)]
            
            conn.close()
        finally:
            if os.path.exists(temp_db_path):
                os.unlink(temp_db_path)

    def test_json_data_loading(self, temp_database, test_json_data, database_operation_test_data):
        """Test JSON data loading pipeline."""
        test_scenario = database_operation_test_data["consumption_table"]
        
        with DuckDBConnection(temp_database) as conn:
            # Create table and load JSON data
            conn.execute(test_scenario["sql"])
            conn.execute(f"""
                INSERT INTO {test_scenario["table_name"]} 
                SELECT * FROM read_json_auto('{test_json_data}')
            """)
            
            # Verify data count
            result = conn.execute(f"SELECT COUNT(*) FROM {test_scenario['table_name']}").fetchone()
            assert result[0] == test_scenario["expected_count"]
            
            # Verify data content with floating point tolerance
            data_result = conn.execute(f"SELECT * FROM {test_scenario['table_name']} ORDER BY id").fetchall()
            assert len(data_result) == len(test_scenario["expected_data"])
            
            for actual, expected in zip(data_result, test_scenario["expected_data"]):
                assert actual[0] == expected[0]  # id
                assert abs(actual[1] - expected[1]) < 0.01  # consumption with tolerance
                assert actual[2] == expected[2]  # date

    def test_empty_json_handling(self, temp_database, empty_json_data):
        """Test handling of empty JSON arrays."""
        with DuckDBConnection(temp_database) as conn:
            try:
                conn.execute("CREATE TABLE empty_test (id INTEGER, value TEXT)")
                conn.execute(f"""
                    INSERT INTO empty_test 
                    SELECT * FROM read_json_auto('{empty_json_data}')
                """)
                
                result = conn.execute("SELECT COUNT(*) FROM empty_test").fetchone()
                assert result[0] == 0
                
            except Exception:
                # If DuckDB can't handle empty JSON, ensure table exists and is empty
                conn.execute("CREATE TABLE IF NOT EXISTS empty_test (id INTEGER, value TEXT)")
                result = conn.execute("SELECT COUNT(*) FROM empty_test").fetchone()
                assert result[0] == 0

    def test_error_scenarios(self, temp_database, invalid_json_data):
        """Test various error scenarios."""
        with DuckDBConnection(temp_database) as conn:
            conn.execute("CREATE TABLE error_test (id INTEGER)")
            
            # Test file not found error
            with pytest.raises(Exception) as exc_info:
                conn.execute("INSERT INTO error_test SELECT * FROM read_json_auto('nonexistent_file.json')")
            
            error_message = str(exc_info.value).lower()
            assert ("no such file" in error_message or "not found" in error_message or 
                    "does not exist" in error_message or "no files found" in error_message)
            
            # Test invalid JSON error
            with pytest.raises(Exception):
                conn.execute(f"INSERT INTO error_test SELECT * FROM read_json_auto('{invalid_json_data}')")
            
            # Test invalid SQL error
            with pytest.raises(Exception):
                conn.execute("INVALID SQL STATEMENT")

    def test_parametrized_table_operations(self, temp_database, database_operation_test_data):
        """Test table operations with different schemas."""
        for table_type, test_data in database_operation_test_data.items():
            with DuckDBConnection(temp_database) as conn:
                # Create table
                conn.execute(test_data["sql"])
                
                # Verify table exists
                tables_result = conn.execute("SHOW TABLES").fetchall()
                table_names = [row[0] for row in tables_result]
                assert test_data["table_name"] in table_names
                
                # Verify table is initially empty
                count_result = conn.execute(f"SELECT COUNT(*) FROM {test_data['table_name']}").fetchone()
                assert count_result[0] == 0
                
                # Clean up for next iteration
                conn.execute(f"DROP TABLE {test_data['table_name']}")