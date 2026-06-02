import os
import tempfile
from contextlib import nullcontext as does_not_raise

import pytest

from utils.configuration_classes import (
    DataGouvConfiguration,
    EconomieGouvConfiguration,
)
from utils.database import DuckDBConnection
from utils.files import load_json, save_json


class TestEndToEndPipelines:
    """End-to-end pipeline testing with real workflows and content verification."""

    @pytest.fixture
    def temp_db_file(self):
        """Temporary database file."""
        temp_dir = tempfile.gettempdir()
        db_path = os.path.join(temp_dir, f"pipeline_test_{os.getpid()}.db")
        yield db_path
        if os.path.exists(db_path):
            os.unlink(db_path)

    @pytest.fixture
    def temp_json_file(self):
        """Temporary JSON file."""
        temp_dir = tempfile.gettempdir()
        json_path = os.path.join(temp_dir, f"pipeline_data_{os.getpid()}.json")
        yield json_path
        if os.path.exists(json_path):
            os.unlink(json_path)

    @pytest.fixture
    def mock_consumption_api_data(self):
        """Mock API response for consumption data."""
        return {
            "data": [
                {"id": 1, "consumption": 150.5, "date": "2024-01-01"},
                {"id": 2, "consumption": 200.3, "date": "2024-01-02"},
                {"id": 3, "consumption": 175.8, "date": "2024-01-03"},
            ],
            "links": {"next": None},  # No pagination
        }

    @pytest.fixture
    def mock_stations_api_data(self):
        """Mock API response for stations data."""
        return {
            "results": [
                {"id": 1, "latitude": 48.8566, "longitude": 2.3522, "ville": "Paris"},
                {"id": 2, "latitude": 45.7640, "longitude": 4.8357, "ville": "Lyon"},
                {
                    "id": 3,
                    "latitude": 43.2965,
                    "longitude": 5.3698,
                    "ville": "Marseille",
                },
            ],
            "total_count": 3,
        }

    @pytest.fixture
    def consumption_config_fixture(self):
        """Data.gouv configuration for consumption pipeline."""
        return DataGouvConfiguration(
            api_type="data_gouv",
            dataset="test-consumption-dataset",
            target_file="test_consumption.json",
            sql_file="fixtures/sql/test_consumption.sql",
            sql_creation="CREATE TABLE consumption (id INTEGER, consumption REAL, date TEXT)",
            table_name="consumption",
        )

    @pytest.fixture
    def stations_config_fixture(self):
        """Economie.gouv configuration for stations pipeline."""
        return EconomieGouvConfiguration(
            api_type="economie_gouv",
            dataset="test-stations-dataset",
            target_file="test_stations.json",
            sql_file="fixtures/sql/test_stations.sql",
            sql_creation="CREATE TABLE stations (id INTEGER, latitude REAL, longitude REAL, ville TEXT)",
            table_name="stations",
            select=["id", "latitude", "longitude", "ville"],
        )

    @pytest.mark.parametrize(
        "config_fixture, api_data_fixture, expected_records, expectation",
        [
            (
                "consumption_config_fixture",
                "mock_consumption_api_data",
                3,
                does_not_raise(),
            ),
            ("stations_config_fixture", "mock_stations_api_data", 3, does_not_raise()),
        ],
    )
    def test_complete_data_pipeline_workflow(
        self,
        request,
        temp_db_file,
        temp_json_file,
        config_fixture,
        api_data_fixture,
        expected_records,
        expectation,
    ):
        """Test complete pipeline: API → JSON → Database → Verification."""
        config = request.getfixturevalue(config_fixture)
        api_data = request.getfixturevalue(api_data_fixture)

        with expectation:
            # Step 1: Simulate API data fetch and save to JSON
            if config.api_type == "data_gouv":
                data_to_save = api_data["data"]
            else:  # economie_gouv
                data_to_save = api_data["results"]

            save_json(data_to_save, temp_json_file)

            # Step 2: Verify JSON file content
            assert os.path.exists(temp_json_file)
            saved_data = load_json(temp_json_file)
            assert len(saved_data) == expected_records

            # Step 3: Create database and table
            with DuckDBConnection(temp_db_file) as conn:
                conn.execute(config.sql_creation)

                # Verify table was created
                tables = conn.execute("SHOW TABLES").fetchall()
                table_names = [table[0] for table in tables]
                assert config.table_name in table_names

                # Step 4: Load JSON data into database
                conn.execute(f"""
                    INSERT INTO {config.table_name}
                    SELECT * FROM read_json_auto('{temp_json_file}')
                """)

                # Step 5: Verify data in database
                count_result = conn.execute(
                    f"SELECT COUNT(*) FROM {config.table_name}"
                ).fetchone()
                assert count_result[0] == expected_records

                # Step 6: Verify specific data content
                all_data = conn.execute(
                    f"SELECT * FROM {config.table_name} ORDER BY id"
                ).fetchall()
                assert len(all_data) == expected_records
                assert all_data[0][0] == 1  # First record ID should be 1

    def test_consumption_pipeline_data_integrity(
        self,
        temp_db_file,
        temp_json_file,
        consumption_config_fixture,
        mock_consumption_api_data,
    ):
        """Test consumption pipeline with detailed data integrity checks."""
        config = consumption_config_fixture
        api_data = mock_consumption_api_data

        # Save API data
        save_json(api_data["data"], temp_json_file)

        with DuckDBConnection(temp_db_file) as conn:
            # Create table and insert data
            conn.execute(config.sql_creation)
            conn.execute(
                f"INSERT INTO {config.table_name} SELECT * FROM read_json_auto('{temp_json_file}')"
            )

            # Verify consumption calculations
            avg_consumption = conn.execute(
                f"SELECT AVG(consumption) FROM {config.table_name}"
            ).fetchone()[0]
            expected_avg = (150.5 + 200.3 + 175.8) / 3
            assert abs(avg_consumption - expected_avg) < 0.01

            # Verify date range
            date_range = conn.execute(
                f"SELECT MIN(date), MAX(date) FROM {config.table_name}"
            ).fetchone()
            assert date_range[0] == "2024-01-01"
            assert date_range[1] == "2024-01-03"

            # Verify specific consumption values
            high_consumption = conn.execute(
                f"SELECT * FROM {config.table_name} WHERE consumption > 200"
            ).fetchall()
            assert len(high_consumption) == 1
            assert abs(high_consumption[0][1] - 200.3) < 0.01

    def test_stations_pipeline_geographic_data(
        self,
        temp_db_file,
        temp_json_file,
        stations_config_fixture,
        mock_stations_api_data,
    ):
        """Test stations pipeline with geographic data validation."""
        config = stations_config_fixture
        api_data = mock_stations_api_data

        # Save API data
        save_json(api_data["results"], temp_json_file)

        with DuckDBConnection(temp_db_file) as conn:
            # Create table and insert data
            conn.execute(config.sql_creation)
            conn.execute(
                f"INSERT INTO {config.table_name} SELECT * FROM read_json_auto('{temp_json_file}')"
            )

            # Verify geographic coordinates
            paris_data = conn.execute(
                f"SELECT * FROM {config.table_name} WHERE ville = 'Paris'"
            ).fetchone()
            assert abs(paris_data[1] - 48.8566) < 0.01  # latitude
            assert abs(paris_data[2] - 2.3522) < 0.01  # longitude

            # Verify city count
            city_count = conn.execute(
                f"SELECT COUNT(DISTINCT ville) FROM {config.table_name}"
            ).fetchone()[0]
            assert city_count == 3

            # Verify coordinate ranges (France)
            coord_ranges = conn.execute(f"""
                SELECT MIN(latitude), MAX(latitude), MIN(longitude), MAX(longitude)
                FROM {config.table_name}
            """).fetchone()
            min_lat, max_lat, min_lon, max_lon = coord_ranges

            # France coordinate ranges validation
            assert 41 <= min_lat <= 51  # France latitude range
            assert 41 <= max_lat <= 51
            assert -5 <= min_lon <= 10  # France longitude range
            assert -5 <= max_lon <= 10

    def test_configuration_to_database_integration(self, temp_db_file):
        """Test configuration manager integration with database operations."""
        # Create a test configuration
        config_data = {
            "api_type": "data_gouv",
            "dataset": "test-dataset",
            "target_file": "test_table.json",
            "sql_file": "fixtures/sql/test_consumption.sql",
            "sql_creation": "CREATE TABLE test_table (id INTEGER, value TEXT)",
            "table_name": "test_table",
        }

        # Create configuration object
        config = DataGouvConfiguration(**config_data)

        # Test database integration
        with DuckDBConnection(temp_db_file) as conn:
            # Use configuration to create table
            conn.execute(config.sql_creation)

            # Verify table creation
            tables = conn.execute("SHOW TABLES").fetchall()
            table_names = [table[0] for table in tables]
            assert config.table_name in table_names

            # Test table schema
            schema = conn.execute(f"DESCRIBE {config.table_name}").fetchall()
            schema_dict = {col[0]: col[1] for col in schema}
            assert "id" in schema_dict
            assert "value" in schema_dict

    @pytest.mark.parametrize(
        "error_scenario, expectation",
        [
            ("missing_json_file", pytest.raises(Exception)),
            ("invalid_sql", pytest.raises(Exception)),
            ("wrong_table_name", pytest.raises(Exception)),
        ],
    )
    def test_pipeline_error_scenarios(
        self, temp_db_file, consumption_config_fixture, error_scenario, expectation
    ):
        """Test pipeline error handling scenarios."""
        config = consumption_config_fixture

        with expectation:
            with DuckDBConnection(temp_db_file) as conn:
                if error_scenario == "missing_json_file":
                    # Try to load from non-existent file
                    conn.execute(config.sql_creation)
                    conn.execute(
                        f"INSERT INTO {config.table_name} SELECT * FROM read_json_auto('nonexistent.json')"
                    )

                elif error_scenario == "invalid_sql":
                    # Try invalid SQL
                    conn.execute("CREATE TABLE invalid syntax here")

                elif error_scenario == "wrong_table_name":
                    # Try to insert into non-existent table
                    conn.execute("INSERT INTO wrong_table_name VALUES (1, 'test')")

    def test_multi_pipeline_database_sharing(
        self,
        temp_db_file,
        temp_json_file,
        consumption_config_fixture,
        stations_config_fixture,
        mock_consumption_api_data,
        mock_stations_api_data,
    ):
        """Test multiple pipelines sharing the same database."""
        consumption_config = consumption_config_fixture
        stations_config = stations_config_fixture

        with DuckDBConnection(temp_db_file) as conn:
            # Create both tables
            conn.execute(consumption_config.sql_creation)
            conn.execute(stations_config.sql_creation)

            # Load consumption data
            save_json(mock_consumption_api_data["data"], temp_json_file)
            conn.execute(
                f"INSERT INTO {consumption_config.table_name} SELECT * FROM read_json_auto('{temp_json_file}')"
            )

            # Load stations data (overwrite temp file)
            save_json(mock_stations_api_data["results"], temp_json_file)
            conn.execute(
                f"INSERT INTO {stations_config.table_name} SELECT * FROM read_json_auto('{temp_json_file}')"
            )

            # Verify both tables have data
            consumption_count = conn.execute(
                f"SELECT COUNT(*) FROM {consumption_config.table_name}"
            ).fetchone()[0]
            stations_count = conn.execute(
                f"SELECT COUNT(*) FROM {stations_config.table_name}"
            ).fetchone()[0]

            assert consumption_count == 3
            assert stations_count == 3

            # Verify table independence
            tables = conn.execute("SHOW TABLES").fetchall()
            table_names = [table[0] for table in tables]
            assert consumption_config.table_name in table_names
            assert stations_config.table_name in table_names
            assert len(table_names) == 2
