import json
import sys
from pathlib import Path
from datetime import datetime
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

def load_config():
    """Load config from secrets/config.json"""
    config_path = Path("secrets/config.json")
    with open(config_path, 'r') as f:
        return json.load(f)

def create_test_catalog():
    """Create test catalog"""
    return ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(
                    name="users",
                    json_schema={
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "email": {"type": "string"},
                            "avatar": {"type": "string"}
                        }
                    },
                    supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental]
                ),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.overwrite
            ),
            ConfiguredAirbyteStream(
                stream=AirbyteStream(
                    name="deals",
                    json_schema={
                        "type": "object", 
                        "properties": {
                            "name": {"type": "string"},
                            "avatar": {"type": "string"}
                        }
                    },
                    supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental]
                ),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.overwrite
            )
        ]
    )

def create_test_messages():
    """Create test messages from source"""
    return [
        AirbyteMessage(
            type=Type.RECORD,
            record=AirbyteRecordMessage(
                stream="users",
                data={
                    "name": "John Doe from Test",
                    "email": "john.test@example.com",
                    "avatar": "https://example.com/john.jpg"
                },
                emitted_at=int(datetime.now().timestamp() * 1000)
            )
        ),
        AirbyteMessage(
            type=Type.RECORD,
            record=AirbyteRecordMessage(
                stream="users", 
                data={
                    "name": "Jane Smith from Test",
                    "email": "jane.test@example.com",
                    "avatar": "https://example.com/jane.jpg"
                },
                emitted_at=int(datetime.now().timestamp() * 1000)
            )
        ),
        AirbyteMessage(
            type=Type.RECORD,
            record=AirbyteRecordMessage(
                stream="deals",
                data={
                    "name": "Big Test Deal",
                    "avatar": "https://example.com/deal.jpg"
                },
                emitted_at=int(datetime.now().timestamp() * 1000)
            )
        )
    ]

def main():
    print("🚀 Testing MockAPI Destination Connector")
    print("=" * 50)
    
    try:
        # Load configuration
        config = load_config()
        print(f"✅ Config loaded: {config['api_url']}")
        
        # Create destination instance
        destination = DestinationMockapi()
        
        # Test connection
        print("\n📡 Testing connection...")
        connection_result = destination.check(None, config)
        if connection_result.status.name == "SUCCEEDED":
            print("✅ Connection successful!")
        else:
            print(f"❌ Connection failed: {connection_result.message}")
            return
        
        # Create catalog and messages
        catalog = create_test_catalog()
        messages = create_test_messages()
        
        print(f"\n📝 Processing {len(messages)} test records...")
        
        # Write data (this simulates what Airbyte does)
        output_messages = list(destination.write(config, catalog, messages))
        
        print(f"✅ Successfully processed {len(output_messages)} messages")
        print("\n🎉 Test completed! Check your MockAPI to see the new records:")
        print(f"   Users: {config['api_url']}/users")
        print(f"   Deals: {config['api_url']}/deals")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
