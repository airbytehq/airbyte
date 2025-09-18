import pytest
from unittest.mock import Mock, patch
from destination_mockapi.writer import MockAPIWriter

class TestMockAPIWriter:
    
    @pytest.fixture
    def mock_client(self):
        client = Mock()
        client.create_user.return_value = {"id": "123", "name": "Test User"}
        client.create_deal.return_value = {"id": "456", "title": "Test Deal"}
        return client
    
    @pytest.fixture
    def writer(self, mock_client):
        return MockAPIWriter(client=mock_client, batch_size=2)
    
    def test_write_user_record(self, writer, mock_client):
        """Test writing a user record"""
        user_record = {
            "name": "John Doe",
            "email": "john@example.com",
            "age": 30
        }
        
        writer.write_record("users", user_record)
        writer.flush()
        
        mock_client.create_user.assert_called_once()
    
    def test_write_deal_record(self, writer, mock_client):
        """Test writing a deal record"""
        deal_record = {
            "title": "Big Deal",
            "amount": 10000,
            "stage": "negotiation"
        }
        
        writer.write_record("deals", deal_record)
        writer.flush()
        
        mock_client.create_deal.assert_called_once()
    
    def test_batch_processing(self, writer, mock_client):
        """Test batch processing triggers flush"""
        # Write batch_size records to trigger auto-flush
        for i in range(2):
            writer.write_record("users", {"name": f"User {i}"})
        
        # Should have called create_user twice due to batch size
        assert mock_client.create_user.call_count == 2
    
    def test_unknown_stream(self, writer, mock_client, caplog):
        """Test handling of unknown stream"""
        writer.write_record("unknown_stream", {"data": "test"})
        writer.flush()
        
        assert "Unknown stream: unknown_stream" in caplog.text