import logging
from json import JSONDecodeError
import pytest

from utils.configuration_classes import ConfigurationManager, DataGouvConfiguration, EconomieGouvConfiguration


class TestConfigurationManager:
    """
    Configuration Manager test suite using conftest.py fixtures and dynamic fixture resolution.
    
    Following trainer's advanced methodology with request.getfixturevalue() pattern.
    """

    @pytest.mark.parametrize("sql_filename,expected_fixture", [
        pytest.param("fixtures/sql/test_consumption.sql", "select_sql", id="consumption_sql"),
        pytest.param("fixtures/sql/test_stations.sql", "select_sql", id="stations_sql"),
    ])
    def test_load_sql_file_success(self, request, sql_filename, expected_fixture):
        """Test successful SQL file loading using dynamic fixture resolution."""
        result = ConfigurationManager._load_sql_file(sql_filename)
        expected = request.getfixturevalue(expected_fixture)
        assert result == expected

    @pytest.mark.parametrize("sql_filename,expected_exception", [
        pytest.param("nonexistent_file.sql", FileNotFoundError, id="file_not_found"),
        pytest.param("fixtures/sql/missing.sql", FileNotFoundError, id="fixture_not_found"),
    ])
    def test_load_sql_file_failure(self, sql_filename, expected_exception):
        """Test SQL file loading failure scenarios."""
        with pytest.raises(expected_exception):
            ConfigurationManager._load_sql_file(sql_filename)

    @pytest.mark.parametrize("config_file,expected_fixture", [
        pytest.param(
            "tests/fixtures/config/valid_economie_gouv.json",
            "valid_economie_gouv_list",
            id="economie_gouv_single"
        ),
        pytest.param(
            "tests/fixtures/config/valid_data_gouv.json",
            "valid_data_gouv_list",
            id="data_gouv_single"
        ),
        pytest.param(
            "tests/fixtures/config/mixed_configs.json",
            "mixed_configs_list",
            id="mixed_types"
        ),
        pytest.param(
            "tests/fixtures/config/empty_list.json",
            "empty_list",
            id="empty_list"
        ),
    ])
    def test_load_all_configurations_success(self, request, config_file, expected_fixture):
        """Test successful configuration loading using fixture references."""
        result = ConfigurationManager.load_all_configurations(config_file)
        expected = request.getfixturevalue(expected_fixture)
        
        assert isinstance(result, list)
        assert len(result) == len(expected)
        
        # Compare actual objects
        for actual, expect in zip(result, expected):
            assert type(actual) == type(expect)
            assert actual.api_type == expect.api_type
            assert actual.dataset == expect.dataset
            assert actual.table_name == expect.table_name

    @pytest.mark.parametrize("config_file,expected_exception", [
        pytest.param("nonexistent_file.json", FileNotFoundError, id="file_not_found"),
        pytest.param("tests/fixtures/config/empty_config.json", JSONDecodeError, id="empty_file"),
        pytest.param("tests/fixtures/config/invalid_api_type.json", ValueError, id="invalid_api_type"),
    ])
    def test_load_all_configurations_failure(self, config_file, expected_exception):
        """Test configuration loading failure scenarios."""
        with pytest.raises(expected_exception):
            ConfigurationManager.load_all_configurations(config_file)

    @pytest.mark.parametrize("table_name,config_fixture,should_find", [
        pytest.param("test_consumption", "valid_data_gouv_list", True, id="data_gouv_found"),
        pytest.param("test_stations", "valid_economie_gouv_list", True, id="economie_gouv_found"),
        pytest.param("nonexistent_table", "empty_list", False, id="table_not_found"),
    ])
    def test_get_configuration_by_table(self, request, mocked_configuration_manager, 
                                      table_name, config_fixture, should_find):
        """Test configuration retrieval by table name using fixtures."""
        test_configs = request.getfixturevalue(config_fixture)
        
        # Mock the configuration manager
        mocked_configuration_manager.mock_load_all(test_configs)
        
        result = ConfigurationManager.get_configuration_by_table(table_name)
        
        if should_find and test_configs:
            assert result is not None
            assert result.table_name == table_name
        else:
            assert result is None

    @pytest.mark.parametrize("api_type,expected_count", [
        pytest.param("economie_gouv", 1, id="economie_gouv_filter"),
        pytest.param("data_gouv", 1, id="data_gouv_filter"),
        pytest.param("nonexistent_type", 0, id="no_match"),
    ])
    def test_get_configurations_by_api_type(self, mocked_configuration_manager, mixed_configs_list,
                                          api_type, expected_count):
        """Test configuration filtering by API type using fixtures."""
        # Mock the configuration manager with mixed configs
        mocked_configuration_manager.mock_load_all(mixed_configs_list)
        
        result = ConfigurationManager.get_configurations_by_api_type(api_type)
        
        assert isinstance(result, list)
        assert len(result) == expected_count
        
        if expected_count > 0:
            assert all(config.api_type == api_type for config in result)

    def test_config_factory_usage(self, config_factory):
        """Test using the config factory fixture for custom configurations."""
        # Create custom economy gov config
        custom_config = config_factory(
            "economie_gouv",
            dataset="custom_dataset",
            table_name="custom_table",
            select=["custom_field"]
        )
        
        assert isinstance(custom_config, EconomieGouvConfiguration)
        assert custom_config.api_type == "economie_gouv"
        assert custom_config.dataset == "custom_dataset"
        assert custom_config.table_name == "custom_table"
        assert custom_config.select == ["custom_field"]

    def test_config_factory_data_gouv(self, config_factory):
        """Test config factory with data_gouv type."""
        custom_config = config_factory(
            "data_gouv",
            dataset="custom_data_gouv_dataset"
        )
        
        assert isinstance(custom_config, DataGouvConfiguration)
        assert custom_config.api_type == "data_gouv"
        assert custom_config.dataset == "custom_data_gouv_dataset"

    def test_config_factory_invalid_type(self, config_factory):
        """Test config factory with invalid API type."""
        with pytest.raises(ValueError):
            config_factory("invalid_type")

    @pytest.mark.parametrize("fixture_name,expected_type", [
        pytest.param("valid_economie_gouv_config", EconomieGouvConfiguration, id="single_economie_config"),
        pytest.param("valid_data_gouv_config", DataGouvConfiguration, id="single_data_config"),
    ])
    def test_individual_config_fixtures(self, request, fixture_name, expected_type):
        """Test individual configuration fixtures directly."""
        config = request.getfixturevalue(fixture_name)
        
        assert isinstance(config, expected_type)
        assert config.api_type in ["economie_gouv", "data_gouv"]
        assert config.sql_creation == "SELECT 1"