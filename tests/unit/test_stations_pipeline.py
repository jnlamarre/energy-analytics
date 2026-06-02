import json
import logging
from unittest.mock import Mock, mock_open, patch

import pytest

from pipelines.stations import StationsPipeline, StationsProcessor, StationsStorage


class TestStationsProcessor:
    """Test StationsProcessor business logic."""

    def test_constructor_with_logger(self):
        """Test StationsProcessor constructor with provided logger."""
        mock_logger = Mock(spec=logging.Logger)

        processor = StationsProcessor(mock_logger)

        assert processor.table_name == "stations"
        assert processor.logger is mock_logger

    def test_constructor_without_logger(self):
        """Test StationsProcessor constructor creates default logger."""
        processor = StationsProcessor()

        assert processor.table_name == "stations"
        assert isinstance(processor.logger, logging.Logger)
        assert processor.logger.name == "stations_processor"

    def test_process_data_passthrough(self):
        """Test process method returns data unchanged (current implementation)."""
        processor = StationsProcessor()

        test_data = [
            {"id": 1, "name": "Station A", "lat": 48.8566, "lon": 2.3522},
            {"id": 2, "name": "Station B", "lat": 45.764, "lon": 4.8357},
        ]

        result = processor.process(test_data)

        assert result == test_data
        assert result is test_data  # Should be same object (no transformation)


class TestStationsStorage:
    """Test StationsStorage business logic."""

    def test_constructor_with_logger(self):
        """Test StationsStorage constructor with provided logger."""
        mock_logger = Mock(spec=logging.Logger)

        storage = StationsStorage(mock_logger)

        assert storage.table_name == "stations"
        assert storage.logger is mock_logger

    def test_constructor_without_logger(self):
        """Test StationsStorage constructor creates default logger."""
        storage = StationsStorage()

        assert storage.table_name == "stations"
        assert isinstance(storage.logger, logging.Logger)
        assert storage.logger.name == "stations_storage"

    def test_create_table_with_config_sql(self):
        """Test create_table using SQL from configuration."""
        mock_conn = Mock()
        mock_config = Mock()
        mock_config.sql_creation = "CREATE TABLE stations (id BIGINT)"
        mock_config_manager = Mock()

        storage = StationsStorage()
        storage.config_manager = mock_config_manager
        mock_config_manager.get_configuration_by_table.return_value = mock_config

        storage.create_table(mock_conn)

        # Verify sequence of operations
        mock_conn.execute.assert_any_call("DROP TABLE IF EXISTS stations")
        mock_conn.execute.assert_any_call("CREATE TABLE stations (id BIGINT)")
        mock_config_manager.get_configuration_by_table.assert_called_once_with(
            "stations"
        )

    def test_create_table_with_fallback_sql(self):
        """Test create_table using fallback SQL when config has no sql_creation."""
        mock_conn = Mock()
        mock_config = Mock()
        mock_config.sql_creation = None
        mock_config_manager = Mock()

        storage = StationsStorage()
        storage.config_manager = mock_config_manager
        mock_config_manager.get_configuration_by_table.return_value = mock_config

        storage.create_table(mock_conn)

        # Verify fallback SQL was used
        mock_conn.execute.assert_any_call("DROP TABLE IF EXISTS stations")
        # Check that the hardcoded SQL was executed (contains specific fields)
        calls = [str(call) for call in mock_conn.execute.call_args_list]
        assert any("gazole_price DECIMAL" in call for call in calls)
        assert any("latitude DOUBLE" in call for call in calls)

    def test_create_table_no_config_found(self):
        """Test create_table using fallback SQL when no config found."""
        mock_conn = Mock()
        mock_config_manager = Mock()

        storage = StationsStorage()
        storage.config_manager = mock_config_manager
        mock_config_manager.get_configuration_by_table.return_value = None

        storage.create_table(mock_conn)

        # Verify fallback SQL was used
        mock_conn.execute.assert_any_call("DROP TABLE IF EXISTS stations")
        # Should use hardcoded SQL when no config
        calls = [str(call) for call in mock_conn.execute.call_args_list]
        assert any("gazole_price DECIMAL" in call for call in calls)

    def test_insert_data_successful(self):
        """Test successful data insertion with file validation."""
        mock_logger = Mock(spec=logging.Logger)
        mock_conn = Mock()
        mock_fetchone_result = (150,)  # 150 records
        mock_conn.execute.return_value.fetchone.return_value = mock_fetchone_result

        # Mock file operations
        test_data = [{"id": 1, "name": "Station A"}]

        storage = StationsStorage(mock_logger)

        with (
            patch("os.path.exists") as mock_exists,
            patch(
                "builtins.open", mock_open(read_data=json.dumps(test_data))
            ) as mock_file,
            patch("json.load") as mock_json,
        ):
            mock_exists.return_value = True
            mock_json.return_value = test_data

            result = storage.insert_data(mock_conn, "/path/to/stations.json")

            assert result == 150

            # Verify file existence check
            mock_exists.assert_called_once_with("/path/to/stations.json")

            # Verify file was opened and read
            mock_file.assert_called_once_with(
                "/path/to/stations.json", "r", encoding="utf-8"
            )

            # Verify SQL execution
            calls = mock_conn.execute.call_args_list
            assert len(calls) == 2  # INSERT + COUNT

            # Verify INSERT SQL contains the file path and field mapping
            insert_call = str(calls[0])
            assert "/path/to/stations.json" in insert_call
            assert "INSERT INTO stations" in insert_call
            assert "cp as postal_code" in insert_call  # Field mapping
            assert "adresse as address" in insert_call

            # Verify COUNT query
            count_call = str(calls[1])
            assert "SELECT COUNT(*)" in count_call

            # Verify logging
            mock_logger.info.assert_any_call(
                "Loading station data from /path/to/stations.json..."
            )
            mock_logger.info.assert_any_call("Loaded 150 station records")

    def test_insert_data_file_not_found(self):
        """Test insert_data raises error when file doesn't exist."""
        mock_conn = Mock()
        storage = StationsStorage()

        with patch("os.path.exists") as mock_exists:
            mock_exists.return_value = False

            with pytest.raises(
                FileNotFoundError, match="Data file not found: /nonexistent.json"
            ):
                storage.insert_data(mock_conn, "/nonexistent.json")

    def test_insert_data_empty_file(self):
        """Test insert_data handles empty JSON file."""
        mock_logger = Mock(spec=logging.Logger)
        mock_conn = Mock()

        storage = StationsStorage(mock_logger)

        with (
            patch("os.path.exists") as mock_exists,
            patch("builtins.open", mock_open(read_data="[]")),
            patch("json.load") as mock_json,
        ):
            mock_exists.return_value = True
            mock_json.return_value = []  # Empty data

            result = storage.insert_data(mock_conn, "/path/to/empty.json")

            assert result == 0

            # Verify warning was logged
            mock_logger.warning.assert_called_once_with(
                "No data to import (empty JSON file)"
            )

            # Should not execute INSERT
            mock_conn.execute.assert_not_called()

    def test_insert_data_corrupted_file(self):
        """Test insert_data handles corrupted JSON file."""
        mock_logger = Mock(spec=logging.Logger)
        mock_conn = Mock()

        storage = StationsStorage(mock_logger)

        with (
            patch("os.path.exists") as mock_exists,
            patch("builtins.open", mock_open(read_data="invalid json")),
            patch("json.load") as mock_json,
        ):
            mock_exists.return_value = True
            mock_json.side_effect = json.JSONDecodeError("Invalid", "", 0)

            result = storage.insert_data(mock_conn, "/path/to/corrupt.json")

            assert result == 0

            # Verify error was logged
            mock_logger.error.assert_called_once_with(
                "Cannot read data file or file is corrupted"
            )

            # Should not execute INSERT
            mock_conn.execute.assert_not_called()


class TestStationsPipeline:
    """Test StationsPipeline business logic and orchestration."""

    def test_constructor_with_logger(self):
        """Test StationsPipeline constructor with provided logger."""
        mock_logger = Mock(spec=logging.Logger)

        pipeline = StationsPipeline(mock_logger)

        assert pipeline.table_name == "stations"
        assert pipeline.logger is mock_logger
        assert isinstance(pipeline.processor, StationsProcessor)
        assert isinstance(pipeline.storage, StationsStorage)

    def test_constructor_without_logger(self):
        """Test StationsPipeline constructor creates default logger."""
        pipeline = StationsPipeline()

        assert pipeline.table_name == "stations"
        assert isinstance(pipeline.logger, logging.Logger)
        assert pipeline.logger.name == "stations_pipeline"

    def test_fetch_successful(self):
        """Test fetch with successful API call."""
        mock_logger = Mock(spec=logging.Logger)
        mock_config = Mock()
        mock_config.url = "http://api.test?limit={step}&offset={offset}"

        with (
            patch("pipelines.stations.ConfigurationManager") as mock_config_mgr,
            patch("pipelines.stations.fetch_paginated_api") as mock_fetch,
        ):
            mock_config_mgr.get_configuration_by_table.return_value = mock_config
            mock_fetch.return_value = [
                {"id": 1, "name": "Station A"},
                {"id": 2, "name": "Station B"},
            ]

            pipeline = StationsPipeline(mock_logger)

            result = pipeline.fetch()

            assert len(result) == 2
            assert result[0]["id"] == 1
            assert result[1]["id"] == 2

            # Verify configuration lookup
            mock_config_mgr.get_configuration_by_table.assert_called_once_with(
                "stations"
            )

            # Verify API call with URL template conversion
            expected_url = "http://api.test?limit={limit}&offset={offset}"
            mock_fetch.assert_called_once_with(
                expected_url, limit=100, max_records=10000
            )

            # Verify logging
            mock_logger.info.assert_any_call("Fetching station data...")
            mock_logger.info.assert_any_call("Total stations fetched: 2")

    def test_fetch_no_configuration_found(self):
        """Test fetch raises error when no configuration found."""
        with patch("pipelines.stations.ConfigurationManager") as mock_config_mgr:
            mock_config_mgr.get_configuration_by_table.return_value = None

            pipeline = StationsPipeline()

            with pytest.raises(
                ValueError, match="No configuration found for stations table"
            ):
                pipeline.fetch()

    def test_fetch_url_template_conversion(self):
        """Test fetch correctly converts {step} to {limit} in URL template."""
        mock_config = Mock()
        mock_config.url = "http://api.example.com/data?step={step}&offset={offset}"

        with (
            patch("pipelines.stations.ConfigurationManager") as mock_config_mgr,
            patch("pipelines.stations.fetch_paginated_api") as mock_fetch,
        ):
            mock_config_mgr.get_configuration_by_table.return_value = mock_config
            mock_fetch.return_value = []

            pipeline = StationsPipeline()

            pipeline.fetch()

            # Verify URL template was converted correctly
            expected_url = "http://api.example.com/data?step={limit}&offset={offset}"
            mock_fetch.assert_called_once_with(
                expected_url, limit=100, max_records=10000
            )

    def test_process_delegates_to_processor(self):
        """Test process method delegates to processor."""
        test_data = [{"id": 1, "name": "Station A"}]

        pipeline = StationsPipeline()

        # Mock the processor
        pipeline.processor = Mock()
        pipeline.processor.process.return_value = test_data

        result = pipeline.process(test_data)

        assert result == test_data
        pipeline.processor.process.assert_called_once_with(test_data)

    def test_store_delegates_to_processor(self):
        """Test store method delegates to processor."""
        test_data = [{"id": 1, "name": "Station A"}]

        pipeline = StationsPipeline()

        # Mock the processor
        pipeline.processor = Mock()

        pipeline.store(test_data, "/custom/path.json")

        pipeline.processor.save_to_file.assert_called_once_with(
            test_data, "/custom/path.json"
        )

    def test_load_to_database_delegates_to_storage(self):
        """Test load_to_database method delegates to storage."""
        pipeline = StationsPipeline()

        # Mock the storage
        pipeline.storage = Mock()

        pipeline.load_to_database("/custom/db.path")

        pipeline.storage.load_to_database.assert_called_once_with("/custom/db.path")
