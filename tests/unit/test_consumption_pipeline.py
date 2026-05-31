import pytest
import logging
from unittest.mock import Mock, patch, MagicMock
from contextlib import nullcontext as does_not_raise

from pipelines.consumption import ConsumptionPipeline, ConsumptionProcessor, ConsumptionStorage


class TestConsumptionProcessor:
    """Test ConsumptionProcessor business logic."""
    
    def test_constructor_with_logger(self):
        """Test ConsumptionProcessor constructor with provided logger."""
        mock_logger = Mock(spec=logging.Logger)
        
        processor = ConsumptionProcessor(mock_logger)
        
        assert processor.table_name == "consumption"
        assert processor.logger is mock_logger
    
    def test_constructor_without_logger(self):
        """Test ConsumptionProcessor constructor creates default logger."""
        processor = ConsumptionProcessor()
        
        assert processor.table_name == "consumption"
        assert isinstance(processor.logger, logging.Logger)
        assert processor.logger.name == "consumption_processor"
    
    def test_process_data_passthrough(self):
        """Test process method returns data unchanged (current implementation)."""
        processor = ConsumptionProcessor()
        
        test_data = [
            {"id": 1, "consumption": 100},
            {"id": 2, "consumption": 200}
        ]
        
        result = processor.process(test_data)
        
        assert result == test_data
        assert result is test_data  # Should be same object (no transformation)


class TestConsumptionStorage:
    """Test ConsumptionStorage business logic."""
    
    def test_constructor_with_logger(self):
        """Test ConsumptionStorage constructor with provided logger."""
        mock_logger = Mock(spec=logging.Logger)
        
        storage = ConsumptionStorage(mock_logger)
        
        assert storage.table_name == "consumption"
        assert storage.logger is mock_logger
    
    def test_constructor_without_logger(self):
        """Test ConsumptionStorage constructor creates default logger."""
        storage = ConsumptionStorage()
        
        assert storage.table_name == "consumption"
        assert isinstance(storage.logger, logging.Logger)
        assert storage.logger.name == "consumption_storage"
    
    def test_create_table_with_config_sql(self):
        """Test create_table using SQL from configuration."""
        mock_conn = Mock()
        mock_config = Mock()
        mock_config.sql_creation = "CREATE TABLE consumption (id INTEGER)"
        mock_config_manager = Mock()
        
        storage = ConsumptionStorage()
        storage.config_manager = mock_config_manager
        mock_config_manager.get_configuration_by_table.return_value = mock_config
        
        storage.create_table(mock_conn)
        
        # Verify sequence of operations
        mock_conn.execute.assert_any_call("DROP TABLE IF EXISTS consumption")
        mock_conn.execute.assert_any_call("CREATE TABLE consumption (id INTEGER)")
        mock_config_manager.get_configuration_by_table.assert_called_once_with('consumption')
    
    def test_create_table_with_fallback_sql(self):
        """Test create_table using fallback SQL when config has no sql_creation."""
        mock_conn = Mock()
        mock_config = Mock()
        mock_config.sql_creation = None
        mock_config_manager = Mock()
        
        storage = ConsumptionStorage()
        storage.config_manager = mock_config_manager
        mock_config_manager.get_configuration_by_table.return_value = mock_config
        
        storage.create_table(mock_conn)
        
        # Verify fallback SQL was used
        mock_conn.execute.assert_any_call("DROP TABLE IF EXISTS consumption")
        # Check that the hardcoded SQL was executed (contains specific fields)
        calls = [str(call) for call in mock_conn.execute.call_args_list]
        assert any("total_consumption_mw INTEGER" in call for call in calls)
    
    def test_create_table_no_config_found(self):
        """Test create_table using fallback SQL when no config found."""
        mock_conn = Mock()
        mock_config_manager = Mock()
        
        storage = ConsumptionStorage()
        storage.config_manager = mock_config_manager
        mock_config_manager.get_configuration_by_table.return_value = None
        
        storage.create_table(mock_conn)
        
        # Verify fallback SQL was used
        mock_conn.execute.assert_any_call("DROP TABLE IF EXISTS consumption")
        # Should use hardcoded SQL when no config
        calls = [str(call) for call in mock_conn.execute.call_args_list]
        assert any("total_consumption_mw INTEGER" in call for call in calls)
    
    def test_insert_data_successful(self):
        """Test successful data insertion with count return."""
        mock_conn = Mock()
        mock_result = Mock()
        mock_result.fetchone.return_value = (42,)  # 42 records
        mock_conn.execute.return_value = mock_result
        
        storage = ConsumptionStorage()
        
        result = storage.insert_data(mock_conn, "/path/to/data.json")
        
        assert result == 42
        # Verify SQL execution
        calls = mock_conn.execute.call_args_list
        assert len(calls) == 2  # INSERT + COUNT
        
        # Verify INSERT SQL contains the file path
        insert_call = str(calls[0])
        assert "/path/to/data.json" in insert_call
        assert "INSERT INTO consumption" in insert_call
        
        # Verify COUNT query
        count_call = str(calls[1])
        assert "SELECT COUNT(*)" in count_call
    
    def test_insert_data_no_result(self):
        """Test data insertion when count query returns no result."""
        mock_conn = Mock()
        mock_result = Mock()
        mock_result.fetchone.return_value = None
        mock_conn.execute.return_value = mock_result
        
        storage = ConsumptionStorage()
        
        result = storage.insert_data(mock_conn, "/path/to/data.json")
        
        assert result == 0


class TestConsumptionPipeline:
    """Test ConsumptionPipeline business logic and orchestration."""
    
    def test_constructor_with_logger(self):
        """Test ConsumptionPipeline constructor with provided logger."""
        mock_logger = Mock(spec=logging.Logger)
        
        pipeline = ConsumptionPipeline(mock_logger)
        
        assert pipeline.table_name == "consumption"
        assert pipeline.logger is mock_logger
        assert isinstance(pipeline.processor, ConsumptionProcessor)
        assert isinstance(pipeline.storage, ConsumptionStorage)
    
    def test_constructor_without_logger(self):
        """Test ConsumptionPipeline constructor creates default logger."""
        pipeline = ConsumptionPipeline()
        
        assert pipeline.table_name == "consumption"
        assert isinstance(pipeline.logger, logging.Logger)
        assert pipeline.logger.name == "consumption_pipeline"
    
    def test_fetch_single_date_query(self):
        """Test fetch with single date parameter."""
        mock_logger = Mock(spec=logging.Logger)
        mock_config = Mock()
        mock_config.url = "http://api.test"
        
        with patch('pipelines.consumption.ConfigurationManager') as mock_config_mgr, \
             patch('pipelines.consumption.fetch_with_pagination') as mock_fetch:
            
            mock_config_mgr.get_configuration_by_table.return_value = mock_config
            mock_fetch.return_value = [{"id": 1, "data": "test"}]
            
            pipeline = ConsumptionPipeline(mock_logger)
            
            result = pipeline.fetch(single_date="2026-01-15")
            
            assert result == [{"id": 1, "data": "test"}]
            
            # Verify configuration lookup
            mock_config_mgr.get_configuration_by_table.assert_called_once_with('consumption')
            
            # Verify API call with single date params
            mock_fetch.assert_called_once_with(
                "http://api.test", 
                {'Date__exact': '"2026-01-15"'}
            )
            
            # Verify logging
            mock_logger.info.assert_any_call("Fetching consumption data...")
            mock_logger.info.assert_any_call("Fetching data for single date: 2026-01-15")
    
    def test_fetch_date_range_with_defaults(self):
        """Test fetch with date range using default dates."""
        mock_logger = Mock(spec=logging.Logger)
        mock_config = Mock()
        mock_config.url = "http://api.test"
        
        with patch('pipelines.consumption.ConfigurationManager') as mock_config_mgr, \
             patch('pipelines.consumption.fetch_with_pagination') as mock_fetch:
            
            mock_config_mgr.get_configuration_by_table.return_value = mock_config
            mock_fetch.return_value = [{"id": 1}, {"id": 2}]
            
            pipeline = ConsumptionPipeline(mock_logger)
            
            result = pipeline.fetch()  # No dates provided - should use defaults
            
            assert result == [{"id": 1}, {"id": 2}]
            
            # Verify API call with default date range
            mock_fetch.assert_called_once_with(
                "http://api.test",
                {
                    'Date__greater': "2026-01-01",
                    'Date__less': "2026-03-31"
                }
            )
            
            # Verify logging
            mock_logger.info.assert_any_call("Fetching data for date range: 2026-01-01 to 2026-03-31")
    
    def test_fetch_date_range_custom(self):
        """Test fetch with custom date range."""
        mock_config = Mock()
        mock_config.url = "http://api.test"
        
        with patch('pipelines.consumption.ConfigurationManager') as mock_config_mgr, \
             patch('pipelines.consumption.fetch_with_pagination') as mock_fetch:
            
            mock_config_mgr.get_configuration_by_table.return_value = mock_config
            mock_fetch.return_value = []
            
            pipeline = ConsumptionPipeline()
            
            result = pipeline.fetch(start_date="2026-02-01", end_date="2026-02-28")
            
            assert result == []
            
            # Verify API call with custom dates
            mock_fetch.assert_called_once_with(
                "http://api.test",
                {
                    'Date__greater': "2026-02-01", 
                    'Date__less': "2026-02-28"
                }
            )
    
    def test_fetch_no_configuration_found(self):
        """Test fetch raises error when no configuration found."""
        with patch('pipelines.consumption.ConfigurationManager') as mock_config_mgr:
            mock_config_mgr.get_configuration_by_table.return_value = None
            
            pipeline = ConsumptionPipeline()
            
            with pytest.raises(ValueError, match="No configuration found for consumption table"):
                pipeline.fetch()
    
    def test_fetch_api_exception_handling(self):
        """Test fetch handles API exceptions gracefully."""
        mock_logger = Mock(spec=logging.Logger)
        mock_config = Mock()
        mock_config.url = "http://api.test"
        
        with patch('pipelines.consumption.ConfigurationManager') as mock_config_mgr, \
             patch('pipelines.consumption.fetch_with_pagination') as mock_fetch:
            
            mock_config_mgr.get_configuration_by_table.return_value = mock_config
            mock_fetch.side_effect = Exception("API Error")
            
            pipeline = ConsumptionPipeline(mock_logger)
            
            result = pipeline.fetch(single_date="2026-01-15")
            
            assert result == []  # Should return empty list on error
            
            # Verify error was logged
            mock_logger.error.assert_called_once_with("Error fetching consumption data: API Error")
    
    def test_process_delegates_to_processor(self):
        """Test process method delegates to processor."""
        test_data = [{"id": 1, "data": "test"}]
        
        pipeline = ConsumptionPipeline()
        
        # Mock the processor
        pipeline.processor = Mock()
        pipeline.processor.process.return_value = test_data
        
        result = pipeline.process(test_data)
        
        assert result == test_data
        pipeline.processor.process.assert_called_once_with(test_data)
    
    def test_store_delegates_to_processor(self):
        """Test store method delegates to processor."""
        test_data = [{"id": 1, "data": "test"}]
        
        pipeline = ConsumptionPipeline()
        
        # Mock the processor
        pipeline.processor = Mock()
        
        pipeline.store(test_data, "/custom/path.json")
        
        pipeline.processor.save_to_file.assert_called_once_with(test_data, "/custom/path.json")
    
    def test_load_to_database_delegates_to_storage(self):
        """Test load_to_database method delegates to storage."""
        pipeline = ConsumptionPipeline()
        
        # Mock the storage
        pipeline.storage = Mock()
        
        pipeline.load_to_database("/custom/db.path")
        
        pipeline.storage.load_to_database.assert_called_once_with("/custom/db.path")