import pytest
import json
import os
import logging
from pathlib import Path
from destination_mockapi.client import MockAPIClient
from destination_mockapi.config import get_config_from_dict
from destination_mockapi.destination import DestinationMockapi
from airbyte_cdk.models import Status

class TestMockAPIIntegration:
    
    @pytest.fixture
    def config_from_secrets(self):
        """Load configuration from secrets/config.json"""
        config_path = Path(__file__).parent.parent / "secrets" / "config.json"
        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            # Fallback to environment variable or default
            return {
                "api_url": os.getenv("MOCKAPI_URL", "https://68cc13e1716562cf50764f2b.mockapi.io/api/v1")
            }
    
    @pytest.fixture
    def parsed_config(self, config_from_secrets):
        return get_config_from_dict(config_from_secrets)
    
    @pytest.fixture
    def client(self, parsed_config):
        return MockAPIClient(
            api_url=parsed_config.api_url,
            timeout=parsed_config.timeout
        )
    
    def test_real_connection_with_config(self, client):
        """Test actual connection using config from secrets"""
        result = client.test_connection()
        assert result is True, "Could not connect to MockAPI endpoint from config"
    
    def test_get_existing_users_from_config(self, client):
        """Test fetching existing users using real config"""
        users = client.get_users(limit=5)
        assert isinstance(users, list)
        # Should have existing users since you have 51 users
        assert len(users) > 0
        
        # Check user structure
        if users:
            user = users[0]
            assert "id" in user
    
    def test_destination_check_with_config(self, config_from_secrets):
        """Test destination check method with real config"""
        destination = DestinationMockapi()
        # Use a standard Python logger instead of AirbyteLogger
        logger = logging.getLogger(__name__)
        result = destination.check(logger, config_from_secrets)
        
        assert result.status == Status.SUCCEEDED
    
    @pytest.mark.skip(reason="Only run when you want to test actual data creation")
    def test_create_real_user_with_config(self, client):
        """Test creating a real user using config (use with caution)"""
        test_user = {
            "name": "Test User from Config",
            "email": "testconfig@example.com",
            "age": 25
        }
        
        created_user = client.create_user(test_user)
        assert created_user["name"] == "Test User from Config"
        assert "id" in created_user
        
        client.delete_user(created_user["id"])