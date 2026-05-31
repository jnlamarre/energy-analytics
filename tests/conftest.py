import logging
import pytest
import tempfile
import os

from utils.configuration_classes import ConfigurationManager, DataGouvConfiguration, EconomieGouvConfiguration


# ===== CONFIGURATION FIXTURES =====

# ===== CONFIGURATION INPUT FIXTURES FOR OBJECT TESTING =====

@pytest.fixture(scope="session")
def valid_economie_gouv_input():
    """Input dictionary for valid EconomieGouvConfiguration object creation."""
    return {
        "api_type": "economie_gouv",
        "dataset": "test_dataset",
        "target_file": "test_target.json",
        "sql_file": "fixtures/sql/test_stations.sql",
        "sql_creation": "SELECT 1",
        "table_name": "test_stations",
        "select": ["id", "name"]
    }


@pytest.fixture(scope="session")
def valid_data_gouv_input():
    """Input dictionary for valid DataGouvConfiguration object creation."""
    return {
        "api_type": "data_gouv",
        "dataset": "test_dataset_id",
        "target_file": "test_target.json",
        "sql_file": "fixtures/sql/test_consumption.sql",
        "sql_creation": "SELECT 1",
        "table_name": "test_consumption"
    }


@pytest.fixture
def economie_gouv_missing_required():
    """Input dictionary missing required fields for ValidationError testing."""
    return {
        "api_type": "economie_gouv",
        "dataset": "test_dataset"
        # Missing: target_file, sql_file, sql_creation, table_name, select
    }


@pytest.fixture  
def data_gouv_missing_required():
    """Input dictionary missing required fields for ValidationError testing."""
    return {
        "api_type": "data_gouv",
        "dataset": "test_dataset"
        # Missing: target_file, sql_file, sql_creation, table_name
    }


@pytest.fixture
def economie_gouv_invalid_api_type():
    """Input dictionary with invalid api_type for ValidationError testing."""
    return {
        "api_type": "invalid_type",
        "dataset": "test_dataset",
        "target_file": "test_target.json",
        "sql_file": "fixtures/sql/test_stations.sql", 
        "sql_creation": "SELECT 1",
        "table_name": "test_stations",
        "select": ["id"]
    }


@pytest.fixture
def data_gouv_invalid_api_type():
    """Input dictionary with invalid api_type for ValidationError testing."""
    return {
        "api_type": "invalid_type", 
        "dataset": "test_dataset",
        "target_file": "test_target.json",
        "sql_file": "fixtures/sql/test_consumption.sql",
        "sql_creation": "SELECT 1", 
        "table_name": "test_consumption"
    }


@pytest.fixture
def economie_gouv_with_select(valid_economie_gouv_input):
    """EconomieGouvConfiguration with select fields for URL testing."""
    input_data = valid_economie_gouv_input.copy()
    input_data["select"] = ["id", "name"]
    return EconomieGouvConfiguration(**input_data)


@pytest.fixture
def economie_gouv_empty_select(valid_economie_gouv_input):
    """EconomieGouvConfiguration with empty select list for URL testing."""
    input_data = valid_economie_gouv_input.copy()
    input_data["select"] = []
    return EconomieGouvConfiguration(**input_data)

@pytest.fixture(scope="session")
def valid_economie_gouv_config():
    """Single EconomieGouvConfiguration object for testing. Session-scoped for performance."""
    return EconomieGouvConfiguration(
        api_type="economie_gouv",
        dataset="test_dataset",
        target_file="test_target.json",
        sql_file="fixtures/sql/test_stations.sql",
        sql_creation="SELECT 1",
        table_name="test_stations",
        select=["id", "latitude", "longitude"]
    )


@pytest.fixture(scope="session")
def valid_data_gouv_config():
    """Single DataGouvConfiguration object for testing. Session-scoped for performance."""
    return DataGouvConfiguration(
        api_type="data_gouv", 
        dataset="test_dataset_id",
        target_file="test_target.json",
        sql_file="fixtures/sql/test_consumption.sql",
        sql_creation="SELECT 1",
        table_name="test_consumption"
    )


@pytest.fixture
def valid_economie_gouv_list(valid_economie_gouv_config):
    """List containing single EconomieGouvConfiguration - matches JSON file structure."""
    return [valid_economie_gouv_config]


@pytest.fixture
def valid_data_gouv_list(valid_data_gouv_config):
    """List containing single DataGouvConfiguration - matches JSON file structure."""
    return [valid_data_gouv_config]


@pytest.fixture
def mixed_configs_list():
    """List containing both configuration types - matches mixed_configs.json exactly."""
    economy_config = EconomieGouvConfiguration(
        api_type="economie_gouv",
        dataset="test_stations_dataset",
        target_file="test_stations.json",
        sql_file="fixtures/sql/test_stations.sql",
        sql_creation="SELECT 1",
        table_name="test_stations",
        select=["id", "latitude"]
    )
    
    data_config = DataGouvConfiguration(
        api_type="data_gouv",
        dataset="test_consumption_dataset",
        target_file="test_consumption.json",
        sql_file="fixtures/sql/test_consumption.sql",
        sql_creation="SELECT 1",
        table_name="test_consumption"
    )
    
    return [economy_config, data_config]


@pytest.fixture
def empty_list():
    """Empty list for testing empty configuration scenarios."""
    return []


# ===== SQL CONTENT FIXTURES =====

@pytest.fixture(scope="session")
def select_sql():
    """Simple SQL SELECT statement used in test fixtures. Session-scoped for performance."""
    return "SELECT 1"


# ===== LOGGER FIXTURES =====

@pytest.fixture(scope="session")
def test_logger():
    """Standard logger for testing purposes. Session-scoped for performance."""
    return logging.getLogger("test_fixture")


# ===== CONFIGURATION FACTORY FIXTURE =====

@pytest.fixture(scope="session")
def config_factory():
    """Factory function to create configuration objects with custom parameters. Session-scoped for performance."""
    def _create_config(api_type, **kwargs):
        defaults = {
            "dataset": "test_dataset",
            "target_file": "test.json",
            "sql_file": "fixtures/sql/test_consumption.sql",
            "sql_creation": "SELECT",
            "table_name": "test_table"
        }
        defaults.update(kwargs)
        
        if api_type == "economie_gouv":
            defaults.setdefault("select", ["id"])
            return EconomieGouvConfiguration(api_type=api_type, **defaults)
        elif api_type == "data_gouv":
            return DataGouvConfiguration(api_type=api_type, **defaults)
        else:
            raise ValueError(f"Unsupported API type: {api_type}")
    
    return _create_config


# ===== PARAMETRIZED FIXTURES =====

@pytest.fixture(params=["economie_gouv", "data_gouv"])
def any_api_type(request):
    """Parametrized fixture that yields each API type. Useful for testing both types."""
    return request.param


@pytest.fixture
def any_config(any_api_type, config_factory):
    """Creates a configuration of any type using parametrized fixture."""
    return config_factory(any_api_type)


# ===== DATABASE FIXTURES =====

# ===== DATABASE TEST DATA FIXTURES =====

@pytest.fixture
def test_json_data(tmp_path):
    """Create temporary JSON file with test data for database loading tests."""
    from utils.files import save_json
    
    test_data = [
        {"id": 1, "consumption": 100.5, "date": "2024-01-01"},
        {"id": 2, "consumption": 200.3, "date": "2024-01-02"},
        {"id": 3, "consumption": 150.7, "date": "2024-01-03"}
    ]
    
    json_file = tmp_path / "test_data.json"
    save_json(test_data, str(json_file))
    return str(json_file)


@pytest.fixture
def stations_test_json_data(tmp_path):
    """Create temporary JSON file with stations test data for database loading tests."""
    from utils.files import save_json
    
    stations_data = [
        {"id": 1, "latitude": 48.8566, "longitude": 2.3522, "ville": "Paris"},
        {"id": 2, "latitude": 45.7640, "longitude": 4.8357, "ville": "Lyon"},
        {"id": 3, "latitude": 43.2965, "longitude": 5.3698, "ville": "Marseille"}
    ]
    
    json_file = tmp_path / "test_stations.json"
    save_json(stations_data, str(json_file))
    return str(json_file)


@pytest.fixture
def invalid_json_data(tmp_path):
    """Create temporary file with invalid JSON for error testing."""
    invalid_file = tmp_path / "invalid.json"
    invalid_file.write_text('{"invalid": json content')  # Missing closing brace
    return str(invalid_file)


@pytest.fixture
def empty_json_data(tmp_path):
    """Create temporary JSON file with empty array for edge case testing."""
    from utils.files import save_json
    
    json_file = tmp_path / "empty_data.json"
    save_json([], str(json_file))
    return str(json_file)


@pytest.fixture 
def database_operation_test_data():
    """Fixture providing test data scenarios for database operations."""
    return {
        "consumption_table": {
            "sql": "CREATE TABLE IF NOT EXISTS test_consumption (id INTEGER, consumption REAL, date TEXT)",
            "table_name": "test_consumption",
            "expected_count": 3,
            "expected_data": [(1, 100.5, "2024-01-01"), (2, 200.3, "2024-01-02"), (3, 150.7, "2024-01-03")]
        },
        "stations_table": {
            "sql": "CREATE TABLE IF NOT EXISTS test_stations (id INTEGER, latitude REAL, longitude REAL, ville TEXT)",
            "table_name": "test_stations", 
            "expected_count": 3,
            "expected_data": [(1, 48.8566, 2.3522, "Paris"), (2, 45.7640, 4.8357, "Lyon"), (3, 43.2965, 5.3698, "Marseille")]
        }
    }

@pytest.fixture
def temp_database():
    """Temporary database file for testing. Automatically cleaned up after test."""
    temp_dir = tempfile.gettempdir()
    db_path = os.path.join(temp_dir, f"test_energy_{os.getpid()}.db")
    
    yield db_path
    
    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def database_with_test_data(temp_database):
    """Database with pre-populated test data."""
    from utils.database import DuckDBConnection
    
    with DuckDBConnection(temp_database) as conn:
        conn.execute("CREATE TABLE test_consumption (id INTEGER, consumption REAL)")
        conn.execute("INSERT INTO test_consumption VALUES (1, 100.5), (2, 200.3)")
    
    return temp_database


# ===== API MOCK FIXTURES =====

@pytest.fixture
def mock_api_success_response():
    """Successful API response structure."""
    return {
        'data': [{'id': 1, 'value': 'test'}],
        'links': {'next': None}
    }


@pytest.fixture
def mock_paginated_responses():
    """Multiple API responses for pagination testing."""
    return [
        {'results': [{'id': 1}], 'total_count': 2},
        {'results': [{'id': 2}], 'total_count': 2}
    ]


@pytest.fixture
def mock_empty_api_response():
    """Empty API response for edge case testing."""
    return {
        'data': [],
        'links': {}
    }


# ===== CONFIGURATION MANAGER MOCKING =====

@pytest.fixture
def mocked_configuration_manager():
    """Context manager to temporarily mock ConfigurationManager methods."""
    class MockedConfigManager:
        def __init__(self):
            self.original_load_all = ConfigurationManager.load_all_configurations
            self.original_get_by_table = ConfigurationManager.get_configuration_by_table
            self.original_get_by_type = ConfigurationManager.get_configurations_by_api_type
            
        def mock_load_all(self, configs):
            ConfigurationManager.load_all_configurations = lambda *args: configs
            return self
            
        def restore(self):
            ConfigurationManager.load_all_configurations = self.original_load_all
            ConfigurationManager.get_configuration_by_table = self.original_get_by_table
            ConfigurationManager.get_configurations_by_api_type = self.original_get_by_type
    
    manager = MockedConfigManager()
    yield manager
    manager.restore()