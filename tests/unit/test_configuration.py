import pytest
from contextlib import nullcontext as does_not_raise
from unittest.mock import patch
from pydantic import ValidationError

from utils.configuration_classes import ConfigurationManager, DataGouvConfiguration, EconomieGouvConfiguration


class TestConfigurationObjects:
    """Test configuration object validation and URL generation."""

    @pytest.mark.parametrize(
        "config_fixture, expectation",
        [
            ("valid_economie_gouv_input", does_not_raise()),
            ("economie_gouv_missing_required", pytest.raises(ValidationError))
        ]
    )
    def test_economie_gouv_validation(self, request, config_fixture, expectation):
        """Test EconomieGouvConfiguration validation scenarios."""
        config_data = request.getfixturevalue(config_fixture)
        
        with expectation:
            config = EconomieGouvConfiguration(**config_data)
            assert hasattr(config, 'url')

    @pytest.mark.parametrize(
        "config_fixture, expectation",
        [
            ("valid_data_gouv_input", does_not_raise()),
            ("data_gouv_missing_required", pytest.raises(ValidationError))
        ]
    )
    def test_data_gouv_validation(self, request, config_fixture, expectation):
        """Test DataGouvConfiguration validation scenarios."""
        config_data = request.getfixturevalue(config_fixture)
        
        with expectation:
            config = DataGouvConfiguration(**config_data)
            assert hasattr(config, 'url')

    def test_economie_gouv_url_with_select_fields(self, economie_gouv_with_select):
        """Test URL generation with select fields."""
        url = economie_gouv_with_select.url
        assert "data.economie.gouv.fr" in url
        assert "select=" in url
        for field in economie_gouv_with_select.select:
            assert field in url

    def test_economie_gouv_url_without_select_fields(self, economie_gouv_empty_select):
        """Test URL generation without select fields."""
        url = economie_gouv_empty_select.url
        assert "data.economie.gouv.fr" in url
        # Should not have select parameter or have empty select
        assert "select=" not in url or "select=" in url and url.split("select=")[1].split("&")[0] == ""

    @pytest.mark.parametrize(
        "select_fields, expected_in_url",
        [
            (["id"], ["id"]),
            (["id", "latitude", "longitude"], ["id", "latitude", "longitude"]), 
            ([], [])
        ]
    )
    def test_economie_gouv_select_field_variations(self, config_factory, select_fields, expected_in_url):
        """Test various select field configurations."""
        config = config_factory("economie_gouv", select=select_fields)
        url = config.url
        
        if expected_in_url:
            assert "select=" in url
            for field in expected_in_url:
                assert field in url
        else:
            assert "select=" not in url or url.split("select=")[1].split("&")[0] == ""

    def test_data_gouv_url_generation(self, valid_data_gouv_config):
        """Test DataGouv URL generation."""
        url = valid_data_gouv_config.url
        assert url.startswith("https://tabular-api.data.gouv.fr")
        assert "resources" in url
        assert valid_data_gouv_config.dataset in url

    def test_configuration_object_attributes(self, valid_economie_gouv_config, valid_data_gouv_config):
        """Test that configuration objects have required attributes."""
        # Test EconomieGouv attributes
        assert hasattr(valid_economie_gouv_config, 'api_type')
        assert hasattr(valid_economie_gouv_config, 'dataset')
        assert hasattr(valid_economie_gouv_config, 'select')
        assert hasattr(valid_economie_gouv_config, 'url')
        
        # Test DataGouv attributes  
        assert hasattr(valid_data_gouv_config, 'api_type')
        assert hasattr(valid_data_gouv_config, 'dataset')
        assert hasattr(valid_data_gouv_config, 'url')

    def test_url_template_placeholders(self, valid_economie_gouv_config, valid_data_gouv_config):
        """Test that URLs contain proper placeholders for pagination."""
        economie_url = valid_economie_gouv_config.url
        assert "{step}" in economie_url
        assert "{offset}" in economie_url
        
        # DataGouv doesn't use pagination placeholders
        data_url = valid_data_gouv_config.url
        assert "tabular-api.data.gouv.fr" in data_url

    @pytest.mark.parametrize("api_type", ["economie_gouv", "data_gouv"])
    def test_api_type_consistency(self, config_factory, api_type):
        """Test that api_type is consistent across configuration types."""
        config = config_factory(api_type)
        assert config.api_type == api_type


class TestConfigurationManager:
    """Test ConfigurationManager functionality."""

    def test_load_sql_files(self, select_sql):
        """Test SQL file loading functionality."""
        # This tests the SQL loading capability
        assert select_sql == "SELECT 1"

    def test_load_configurations_success(self, valid_economie_gouv_list, valid_data_gouv_list):
        """Test successful configuration loading."""
        # Test that configurations load properly
        assert len(valid_economie_gouv_list) == 1
        assert len(valid_data_gouv_list) == 1
        
        assert isinstance(valid_economie_gouv_list[0], EconomieGouvConfiguration)
        assert isinstance(valid_data_gouv_list[0], DataGouvConfiguration)

    def test_load_configurations_failure(self, empty_list):
        """Test handling of empty configuration lists."""
        assert len(empty_list) == 0

    def test_configuration_retrieval(self, mixed_configs_list):
        """Test configuration retrieval from mixed lists."""
        assert len(mixed_configs_list) == 2
        
        # Should have both types
        types = [config.api_type for config in mixed_configs_list]
        assert "economie_gouv" in types
        assert "data_gouv" in types

    def test_configuration_objects(self, valid_economie_gouv_config, valid_data_gouv_config):
        """Test configuration object creation."""
        assert valid_economie_gouv_config.api_type == "economie_gouv"
        assert valid_data_gouv_config.api_type == "data_gouv"

    def test_individual_configurations(self, valid_economie_gouv_list, valid_data_gouv_list):
        """Test individual configuration properties."""
        economie_config = valid_economie_gouv_list[0]
        data_config = valid_data_gouv_list[0]
        
        # Test URLs are generated
        assert economie_config.url is not None
        assert data_config.url is not None
        
        # Test required fields exist
        assert economie_config.dataset is not None
        assert data_config.dataset is not None

    def test_target_file_path_resolution_scenarios(self):
        """Test target_file_path resolution for different working directories."""
        from utils.configuration_classes import DataGouvConfiguration, EconomieGouvConfiguration
        
        # Test data
        data_gouv_config = DataGouvConfiguration(
            api_type="data_gouv",
            dataset="test",
            target_file="../data/consumption.json",
            sql_file="consumption.sql", 
            sql_creation="CREATE TABLE test",
            table_name="consumption"
        )
        
        economie_config = EconomieGouvConfiguration(
            api_type="economie_gouv",
            dataset="test",
            target_file="../data/stations.json", 
            sql_file="stations.sql",
            sql_creation="CREATE TABLE test",
            table_name="stations",
            select=[]
        )
        
        # Mock project root scenario (both data and config.json exist)
        with patch('os.path.exists') as mock_exists:
            def exists_side_effect(path):
                return path in ['data', 'config.json']
            mock_exists.side_effect = exists_side_effect
            
            assert data_gouv_config.target_file_path == "data/consumption.json"
            assert economie_config.target_file_path == "data/stations.json"
        
        # Mock src directory scenario (neither exist)
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = False
            
            assert data_gouv_config.target_file_path == "../data/consumption.json"
            assert economie_config.target_file_path == "../data/stations.json"

    def test_configuration_lookup_methods(self):
        """Test configuration lookup by table name and API type."""
        with patch.object(ConfigurationManager, 'load_all_configurations') as mock_load:
            # Mock configurations
            mock_configs = [
                DataGouvConfiguration(
                    api_type="data_gouv", dataset="test", target_file="data1.json",
                    sql_file="test1.sql", sql_creation="CREATE TABLE test1", table_name="consumption"
                ),
                EconomieGouvConfiguration(
                    api_type="economie_gouv", dataset="test", target_file="data2.json", 
                    sql_file="test2.sql", sql_creation="CREATE TABLE test2", table_name="stations",
                    select=[]
                )
            ]
            mock_load.return_value = mock_configs
            
            # Test get_configuration_by_table
            result = ConfigurationManager.get_configuration_by_table("consumption")
            assert result is not None
            assert result.table_name == "consumption"
            assert result.api_type == "data_gouv"
            
            # Test table not found
            result = ConfigurationManager.get_configuration_by_table("nonexistent")
            assert result is None
            
            # Test get_configurations_by_api_type
            data_gouv_configs = ConfigurationManager.get_configurations_by_api_type("data_gouv")
            assert len(data_gouv_configs) == 1
            assert data_gouv_configs[0].api_type == "data_gouv"
            
            economie_configs = ConfigurationManager.get_configurations_by_api_type("economie_gouv")
            assert len(economie_configs) == 1
            assert economie_configs[0].api_type == "economie_gouv"

    def test_sql_file_loading_scenarios(self):
        """Test SQL file loading with different path scenarios."""
        import tempfile
        import os
        
        # Create temporary SQL content
        sql_content = "CREATE TABLE test (id INTEGER);"
        
        # Test standard SQL file loading
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as temp_file:
            temp_file.write(sql_content)
            temp_file_path = temp_file.name
            
        try:
            with patch('os.path.join') as mock_join:
                mock_join.return_value = temp_file_path
                
                result = ConfigurationManager._load_sql_file("test.sql")
                assert result.strip() == sql_content.strip()
                
        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
        # Test fixtures SQL file loading
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as temp_fixture:
            temp_fixture.write(sql_content)
            temp_fixture_path = temp_fixture.name
            
        try:
            with patch('os.path.join') as mock_join:
                mock_join.return_value = temp_fixture_path
                
                result = ConfigurationManager._load_sql_file("fixtures/test.sql")
                assert result.strip() == sql_content.strip()
                
        finally:
            if os.path.exists(temp_fixture_path):
                os.unlink(temp_fixture_path)

    def test_load_configurations_with_unsupported_api_type(self):
        """Test configuration loading with unsupported API type raises error."""
        import tempfile
        import json
        import os
        
        # Create config with unsupported API type
        invalid_config = [
            {
                "api_type": "unsupported_api",
                "dataset": "test",
                "target_file": "test.json",
                "sql_file": "test.sql",
                "table_name": "test"
            }
        ]
        
        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            json.dump(invalid_config, temp_file)
            temp_config_path = temp_file.name
        
        try:
            with patch('os.path.join') as mock_join, \
                 patch.object(ConfigurationManager, '_load_sql_file') as mock_sql:
                mock_join.return_value = temp_config_path
                mock_sql.return_value = "CREATE TABLE test"
                
                with pytest.raises(ValueError, match="Unsupported API type: unsupported_api"):
                    ConfigurationManager.load_all_configurations()
                    
        finally:
            if os.path.exists(temp_config_path):
                os.unlink(temp_config_path)

    def test_load_configurations_complete_flow(self):
        """Test complete configuration loading flow with both API types."""
        import tempfile
        import json
        import os
        
        # Create config with both API types
        complete_config = [
            {
                "api_type": "data_gouv",
                "dataset": "test-data",
                "target_file": "data.json",
                "sql_file": "data.sql",
                "table_name": "data_table"
            },
            {
                "api_type": "economie_gouv", 
                "dataset": "test-economie",
                "target_file": "economie.json",
                "sql_file": "economie.sql", 
                "table_name": "economie_table",
                "select": ["field1", "field2"]
            }
        ]
        
        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            json.dump(complete_config, temp_file)
            temp_config_path = temp_file.name
        
        try:
            with patch('os.path.join') as mock_join, \
                 patch.object(ConfigurationManager, '_load_sql_file') as mock_sql:
                mock_join.return_value = temp_config_path
                mock_sql.return_value = "CREATE TABLE test"
                
                configs = ConfigurationManager.load_all_configurations()
                
                assert len(configs) == 2
                assert any(config.api_type == "data_gouv" for config in configs)
                assert any(config.api_type == "economie_gouv" for config in configs)
                    
        finally:
            if os.path.exists(temp_config_path):
                os.unlink(temp_config_path)