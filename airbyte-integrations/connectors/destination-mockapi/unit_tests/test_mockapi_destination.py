import pytest
from unittest.mock import Mock, patch
from destination_mockapi.destination import DestinationMockapi
from airbyte_cdk.models import AirbyteConnectionStatus, Status

class TestDestinationMockapi:
    
    @pytest.fixture
    def destination(self):
        return DestinationMockapi()
    
    @pytest.fixture
    def valid_config(self):
        return {
            "api_url": "https://68cc13e1716562cf50764f2b.mockapi.io/api/v1",
            "batch_size": 50,
            "timeout": 30
        }
    
    @patch('destination_mockapi.destination.MockAPIClient')
    def test_check_connection_success(self, mock_client_class, destination, valid_config):
        """Test successful connection check"""
        # Setup mock
        mock_client = Mock()
        mock_client.test_connection.return_value = True
        mock_client_class.return_value = mock_client
        
        # Test
        result = destination.check(None, valid_config)
        
        # Assert
        assert result.status == Status.SUCCEEDED
        mock_client.test_connection.assert_called_once()
    
    @patch('destination_mockapi.destination.MockAPIClient')
    def test_check_connection_failure(self, mock_client_class, destination, valid_config):
        """Test connection check failure"""
        # Setup mock
        mock_client = Mock()
        mock_client.test_connection.return_value = False
        mock_client_class.return_value = mock_client
        
        # Test
        result = destination.check(None, valid_config)
        
        # Assert
        assert result.status == Status.FAILED
        assert "Could not connect" in result.message
    
    @patch('destination_mockapi.destination.MockAPIClient')
    def test_check_connection_exception(self, mock_client_class, destination, valid_config):
        """Test connection check with exception"""
        # Setup mock
        mock_client_class.side_effect = Exception("Connection error")
        
        # Test
        result = destination.check(None, valid_config)
        
        # Assert
        assert result.status == Status.FAILED
        assert "Connection failed" in result.message