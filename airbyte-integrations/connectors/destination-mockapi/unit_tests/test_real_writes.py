import pytest
import json
import requests
import time
from datetime import datetime
from pathlib import Path
from airbyte_cdk.models import (
    AirbyteMessage, 
    AirbyteRecordMessage, 
    Type,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    AirbyteStream,
    DestinationSyncMode,
    SyncMode
)
from destination_mockapi.destination import DestinationMockapi

class TestRealMockAPIWrites:
    
    @pytest.fixture
    def config(self):
        """Load real config from secrets"""
        config_path = Path(__file__).parent.parent / "secrets" / "config.json"
        with open(config_path, 'r') as f:
            return json.load(f)
    
    @pytest.fixture
    def destination(self):
        return DestinationMockapi()
    
    @pytest.fixture
    def catalog(self):
        return ConfiguredAirbyteCatalog(
            streams=[
                ConfiguredAirbyteStream(
                    stream=AirbyteStream(
                        name="users",
                        json_schema={"type": "object", "properties": {}},
                        supported_sync_modes=[SyncMode.full_refresh]
                    ),
                    sync_mode=SyncMode.full_refresh,
                    destination_sync_mode=DestinationSyncMode.append
                ),
                ConfiguredAirbyteStream(
                    stream=AirbyteStream(
                        name="deals",
                        json_schema={"type": "object", "properties": {}},
                        supported_sync_modes=[SyncMode.full_refresh]
                    ),
                    sync_mode=SyncMode.full_refresh,
                    destination_sync_mode=DestinationSyncMode.append
                )
            ]
        )
    
    def get_records(self, api_url, endpoint):
        """Get all records from endpoint"""
        response = requests.get(f"{api_url}/{endpoint}")
        response.raise_for_status()
        return response.json()
    
    def delete_record(self, api_url, endpoint, record_id):
        """Delete a specific record"""
        response = requests.delete(f"{api_url}/{endpoint}/{record_id}")
        return response.status_code in [200, 204]
    
    def test_write_users_real_api(self, config, destination, catalog):
        """Test writing users to real MockAPI"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        api_url = config['api_url']
        
        # Get initial count
        initial_users = len(self.get_records(api_url, "users"))
        
        # Create test message
        test_message = AirbyteMessage(
            type=Type.RECORD,
            record=AirbyteRecordMessage(
                stream="users",
                data={
                    "name": f"PyTest User {timestamp}",
                    "email": f"pytest.{timestamp}@example.com",
                    "avatar": "https://randomuser.me/api/portraits/men/99.jpg"
                },
                emitted_at=int(datetime.now().timestamp() * 1000)
            )
        )
        
        # Write the data
        output_messages = list(destination.write(config, catalog, [test_message]))
        
        # Wait for API to process
        time.sleep(1)
        
        # Verify record was created
        final_users = self.get_records(api_url, "users")
        assert len(final_users) == initial_users + 1
        
        # Find our test record
        test_user = None
        for user in final_users:
            if f"PyTest User {timestamp}" in user.get('name', ''):
                test_user = user
                break
        
        assert test_user is not None, "Test user was not found in API"
        assert test_user['name'] == f"PyTest User {timestamp}"
        assert 'id' in test_user
        assert 'createdAt' in test_user
        
        # Cleanup
        self.delete_record(api_url, "users", test_user['id'])
    
    def test_write_deals_real_api(self, config, destination, catalog):
        """Test writing deals to real MockAPI"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        api_url = config['api_url']
        
        # Get initial count
        initial_deals = len(self.get_records(api_url, "deals"))
        
        # Create test message with title->name mapping
        test_message = AirbyteMessage(
            type=Type.RECORD,
            record=AirbyteRecordMessage(
                stream="deals",
                data={
                    "title": f"PyTest Deal {timestamp}",  # Should map to 'name'
                    "amount": 12345,
                    "avatar": "https://logo.clearbit.com/pytest.com"
                },
                emitted_at=int(datetime.now().timestamp() * 1000)
            )
        )
        
        # Write the data
        output_messages = list(destination.write(config, catalog, [test_message]))
        
        # Wait for API to process
        time.sleep(1)
        
        # Verify record was created
        final_deals = self.get_records(api_url, "deals")
        assert len(final_deals) == initial_deals + 1
        
        # Find our test record
        test_deal = None
        for deal in final_deals:
            if f"PyTest Deal {timestamp}" in deal.get('name', ''):
                test_deal = deal
                break
        
        assert test_deal is not None, "Test deal was not found in API"
        assert test_deal['name'] == f"PyTest Deal {timestamp}"  # title was mapped to name
        assert 'id' in test_deal
        assert 'createdAt' in test_deal
        
        # Cleanup
        self.delete_record(api_url, "deals", test_deal['id'])
    
    def test_batch_write_real_api(self, config, destination, catalog):
        """Test writing multiple records in a batch"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        api_url = config['api_url']
        
        # Create multiple test messages
        test_messages = [
            AirbyteMessage(
                type=Type.RECORD,
                record=AirbyteRecordMessage(
                    stream="users",
                    data={
                        "name": f"Batch User {i} {timestamp}",
                        "avatar": f"https://randomuser.me/api/portraits/women/{i+10}.jpg"
                    },
                    emitted_at=int(datetime.now().timestamp() * 1000)
                )
            ) for i in range(3)
        ]
        
        # Get initial count
        initial_users = len(self.get_records(api_url, "users"))
        
        # Write all messages
        output_messages = list(destination.write(config, catalog, test_messages))
        
        # Wait for API to process
        time.sleep(2)
        
        # Verify all records were created
        final_users = self.get_records(api_url, "users")
        assert len(final_users) == initial_users + 3
        
        # Find and cleanup our test records
        test_users = []
        for user in final_users:
            if f"Batch User" in user.get('name', '') and timestamp in user.get('name', ''):
                test_users.append(user)
        
        assert len(test_users) == 3, f"Expected 3 batch users, found {len(test_users)}"
        
        # Cleanup all test records
        for user in test_users:
            self.delete_record(api_url, "users", user['id'])

# Mark these as integration tests that actually write data
pytestmark = pytest.mark.integration