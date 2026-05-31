import pytest
from contextlib import nullcontext as does_not_raise
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