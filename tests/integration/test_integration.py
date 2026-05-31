import pytest
from unittest.mock import Mock, patch
import json
import os

from utils.configuration_classes import ConfigurationManager
from utils.database import DuckDBConnection, execute_query
from utils.files import save_json, load_json


class TestIntegration:
    """
    Integration tests using conftest.py fixtures to test full workflows.
    
    Demonstrates how fixtures enable complex integration testing scenarios.
    """

    def test_configuration_to_database_pipeline(self, temp_database, valid_data_gouv_config):
        """Test complete pipeline: configuration -> SQL -> database."""
        config = valid_data_gouv_config
        
        # Test database creation with config SQL
        with DuckDBConnection(temp_database) as conn:
            conn.execute(config.sql_creation)  # Should execute "SELECT" (harmless)
            
            # Create actual table for testing
            conn.execute("""
                CREATE TABLE test_consumption (
                    id INTEGER,
                    consumption REAL
                )
            """)
            
            # Insert test data
            conn.execute("INSERT INTO test_consumption VALUES (1, 100.5)")
            
            # Verify data
            result = conn.execute("SELECT * FROM test_consumption").fetchall()
            assert len(result) == 1
            assert result[0] == (1, 100.5)

    def test_file_config_database_integration(self, temp_database, mixed_configs_list, tmp_path):
        """Test: save configs to file -> load from file -> use in database operations."""
        # Save configs to temporary JSON file
        config_file = tmp_path / "test_configs.json"
        
        # Convert config objects to dict format (as they would be in JSON)
        config_dicts = []
        for config in mixed_configs_list:
            config_dict = {
                "api_type": config.api_type,
                "dataset": config.dataset,
                "target_file": config.target_file,
                "sql_file": config.sql_file,
                "table_name": config.table_name,
            }
            if hasattr(config, 'select'):
                config_dict["select"] = config.select
            config_dicts.append(config_dict)
        
        save_json(config_dicts, str(config_file))
        
        # Mock SQL file loading to avoid file dependencies
        with patch.object(ConfigurationManager, '_load_sql_file', return_value="SELECT 1"):
            # Load configs back from file
            loaded_configs = ConfigurationManager.load_all_configurations(str(config_file))
            
            assert len(loaded_configs) == 2
            assert loaded_configs[0].api_type == "economie_gouv"
            assert loaded_configs[1].api_type == "data_gouv"

    def test_api_mock_to_file_to_database(self, temp_database, mock_paginated_responses, 
                                        valid_economie_gouv_config, tmp_path):
        """Integration test: Mock API -> Save to file -> Load to database."""
        config = valid_economie_gouv_config
        
        # Step 1: Mock API response and "fetch" data
        mock_api_data = []
        for response in mock_paginated_responses:
            mock_api_data.extend(response['results'])
        
        # Step 2: Save to file (simulating pipeline storage)
        data_file = tmp_path / "api_data.json"
        save_json(mock_api_data, str(data_file))
        
        # Step 3: Load data from file
        loaded_data = load_json(str(data_file))
        assert loaded_data == mock_api_data
        
        # Step 4: Create database table and load data
        with DuckDBConnection(temp_database) as conn:
            # Create table structure
            conn.execute("""
                CREATE TABLE api_test (
                    id INTEGER PRIMARY KEY
                )
            """)
            
            # Insert the loaded data
            for record in loaded_data:
                conn.execute(f"INSERT INTO api_test (id) VALUES ({record['id']})")
            
            # Verify data in database
            result = conn.execute("SELECT COUNT(*) FROM api_test").fetchone()
            assert result[0] == len(mock_api_data)

    def test_configuration_manager_with_database_fixtures(self, database_with_test_data, 
                                                         mocked_configuration_manager,
                                                         valid_data_gouv_config):
        """Test ConfigurationManager with pre-populated database."""
        # Mock configuration manager to return our test config
        mocked_configuration_manager.mock_load_all([valid_data_gouv_config])
        
        # Get config by table name
        config = ConfigurationManager.get_configuration_by_table("test_consumption")
        assert config is not None
        assert config.table_name == "test_consumption"
        
        # Use the config with the test database
        with DuckDBConnection(database_with_test_data) as conn:
            # Verify the test data is there
            result = conn.execute("SELECT COUNT(*) FROM test_consumption").fetchone()
            assert result[0] == 2
            
            # Verify data values (use approximate comparison for floating point)
            result = conn.execute("SELECT * FROM test_consumption ORDER BY id").fetchall()
            assert len(result) == 2
            assert result[0][0] == 1
            assert abs(result[0][1] - 100.5) < 0.01
            assert result[1][0] == 2  
            assert abs(result[1][1] - 200.3) < 0.01

    @pytest.mark.parametrize("config_fixture,expected_api_type", [
        pytest.param("valid_economie_gouv_config", "economie_gouv", id="economie_integration"),
        pytest.param("valid_data_gouv_config", "data_gouv", id="data_integration"),
    ])
    def test_parametrized_integration(self, request, temp_database, config_fixture, expected_api_type):
        """Parametrized integration test using fixture names."""
        config = request.getfixturevalue(config_fixture)
        
        # Verify config properties
        assert config.api_type == expected_api_type
        assert config.sql_creation == "SELECT 1"
        
        # Test database interaction
        with DuckDBConnection(temp_database) as conn:
            # Execute harmless SQL from config
            conn.execute(config.sql_creation)
            
            # Create a test table specific to this config
            table_sql = f"""
                CREATE TABLE {config.table_name}_test (
                    id INTEGER,
                    name TEXT
                )
            """
            conn.execute(table_sql)
            
            # Insert test record
            conn.execute(f"INSERT INTO {config.table_name}_test VALUES (1, '{config.api_type}')")
            
            # Verify
            result = conn.execute(f"SELECT * FROM {config.table_name}_test").fetchone()
            assert result[0] == 1
            assert result[1] == config.api_type

    def test_config_factory_database_integration(self, config_factory, temp_database):
        """Test using config factory with database operations."""
        # Create custom configs using factory
        economy_config = config_factory("economie_gouv", table_name="custom_stations")
        data_config = config_factory("data_gouv", table_name="custom_consumption")
        
        configs = [economy_config, data_config]
        
        # Test each config with database
        with DuckDBConnection(temp_database) as conn:
            for config in configs:
                # Create table for this config
                table_sql = f"""
                    CREATE TABLE {config.table_name} (
                        id INTEGER,
                        api_type TEXT
                    )
                """
                conn.execute(table_sql)
                
                # Insert config info
                conn.execute(f"""
                    INSERT INTO {config.table_name} 
                    VALUES (1, '{config.api_type}')
                """)
            
            # Verify both tables exist and have data
            economy_result = conn.execute("SELECT * FROM custom_stations").fetchone()
            data_result = conn.execute("SELECT * FROM custom_consumption").fetchone()
            
            assert economy_result[1] == "economie_gouv"
            assert data_result[1] == "data_gouv"