import pytest
from unittest.mock import Mock, patch
import requests

from utils.api import fetch_with_pagination, fetch_paginated_api


class TestApi:
    """
    API test suite using conftest.py fixtures for mock responses and test data.
    
    Demonstrates fixture-based testing for API utilities.
    """

    @pytest.mark.parametrize("mock_response_fixture,pagination_key,data_key,expected_total", [
        pytest.param("mock_api_success_response", "next", "data", 1, id="success_response"),
        pytest.param("mock_empty_api_response", "next", "data", 0, id="empty_response"),
    ])
    def test_fetch_with_pagination_fixtures(self, request, mock_response_fixture, 
                                          pagination_key, data_key, expected_total):
        """Test pagination using fixture-based mock responses."""
        mock_data = request.getfixturevalue(mock_response_fixture)
        
        mock_response = Mock()
        mock_response.json.return_value = mock_data
        mock_response.raise_for_status.return_value = None
        
        with patch('requests.get') as mock_get:
            mock_get.return_value = mock_response
            
            result = fetch_with_pagination(
                'http://api.test',
                pagination_key=pagination_key,
                data_key=data_key
            )
            
            assert len(result) == expected_total

    def test_fetch_paginated_api_with_fixture(self, mock_paginated_responses):
        """Test offset-based pagination using fixture responses."""
        mock_responses = []
        for response_data in mock_paginated_responses:
            mock_response = Mock()
            mock_response.json.return_value = response_data
            mock_response.raise_for_status.return_value = None
            mock_responses.append(mock_response)
        
        with patch('requests.get') as mock_get:
            mock_get.side_effect = mock_responses
            
            url_template = 'http://api.test?limit={limit}&offset={offset}'
            result = fetch_paginated_api(url_template, limit=1)
            
            assert len(result) == 2
            assert result == [{'id': 1}, {'id': 2}]
            assert mock_get.call_count == 2

    @pytest.mark.parametrize("exception_type", [
        pytest.param(requests.RequestException("Network error"), id="network_error"),
        pytest.param(requests.ConnectionError("Connection failed"), id="connection_error"),
        pytest.param(requests.Timeout("Request timeout"), id="timeout_error"),
    ])
    def test_fetch_with_pagination_exceptions(self, exception_type):
        """Test API exception handling."""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = exception_type
            
            result = fetch_with_pagination('http://api.test')
            
            assert result == []

    def test_api_integration_with_config_fixture(self, valid_economie_gouv_config):
        """Integration test: API configuration + mocked API response."""
        config = valid_economie_gouv_config
        
        # Mock API response matching the config structure
        mock_response = Mock()
        mock_response.json.return_value = {
            'results': [
                {'id': 1, 'latitude': 48.8566, 'longitude': 2.3522}
            ],
            'total_count': 1
        }
        mock_response.raise_for_status.return_value = None
        
        with patch('requests.get') as mock_get:
            mock_get.return_value = mock_response
            
            # Convert config URL template to match API function format
            # Config uses {step} and {offset}, API function uses {limit} and {offset}
            url_template = config.url.replace('{step}', '{limit}')
            result = fetch_paginated_api(url_template, limit=10)
            
            assert len(result) == 1
            assert result[0]['id'] == 1
            
            # Verify URL was formatted correctly
            expected_url = config.url.format(step=10, offset=0)
            mock_get.assert_called_with(expected_url)

    def test_fetch_with_pagination_no_links(self):
        """Test pagination when response has no links section."""
        mock_response = Mock()
        mock_response.json.return_value = {"data": [{"id": 1}]}  # No 'links' key
        mock_response.raise_for_status.return_value = None
        
        with patch('requests.get') as mock_get:
            mock_get.return_value = mock_response
            
            result = fetch_with_pagination('http://api.test')
            
            assert len(result) == 1
            assert result[0]['id'] == 1

    def test_fetch_paginated_api_no_results(self):
        """Test paginated API when response has empty results."""
        mock_response = Mock()
        mock_response.json.return_value = {"results": [], "total_count": 0}  # Empty results
        mock_response.raise_for_status.return_value = None
        
        with patch('requests.get') as mock_get:
            mock_get.return_value = mock_response
            
            result = fetch_paginated_api('http://api.test?limit={limit}&offset={offset}')
            
            assert len(result) == 0

    def test_fetch_paginated_api_exception_handling(self):
        """Test that fetch_paginated_api handles RequestException properly."""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.RequestException("Network error")
            
            result = fetch_paginated_api('http://api.test?limit={limit}&offset={offset}')
            
            # Should return empty list when exception occurs
            assert len(result) == 0
            # Should have made only one call before breaking
            mock_get.assert_called_once()