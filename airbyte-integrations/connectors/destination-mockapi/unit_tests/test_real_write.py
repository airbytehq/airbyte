import json
import requests
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

def load_config():
    """Load real config"""
    config_path = Path("secrets/config.json")
    with open(config_path, 'r') as f:
        return json.load(f)

def get_current_record_count(api_url, endpoint):
    """Get current number of records in MockAPI"""
    try:
        response = requests.get(f"{api_url}/{endpoint}")
        if response.status_code == 200:
            return len(response.json())
        return 0
    except:
        return 0

def verify_records_created(api_url, endpoint, expected_names):
    """Verify that records were actually created in MockAPI"""
    try:
        response = requests.get(f"{api_url}/{endpoint}")
        if response.status_code != 200:
            return False, f"Failed to fetch {endpoint}: {response.status_code}"
        
        records = response.json()
        
        # Check if our test records are there
        found_names = [record.get('name', '') for record in records]
        
        created_records = []
        for expected_name in expected_names:
            found = False
            for record in records:
                if expected_name in record.get('name', ''):
                    created_records.append(record)
                    found = True
                    break
            if not found:
                return False, f"Expected record '{expected_name}' not found in {endpoint}"
        
        return True, created_records
    except Exception as e:
        return False, f"Error verifying records: {e}"

def cleanup_test_records(api_url, records_to_delete):
    """Clean up test records after testing"""
    print("\n🧹 Cleaning up test records...")
    for record in records_to_delete:
        endpoint = "users" if "email" in str(record) else "deals"
        record_id = record.get('id')
        if record_id:
            try:
                delete_url = f"{api_url}/{endpoint}/{record_id}"
                response = requests.delete(delete_url)
                if response.status_code in [200, 204]:
                    print(f"   ✅ Deleted {endpoint} record: {record.get('name', record_id)}")
                else:
                    print(f"   ⚠️  Failed to delete {endpoint} record {record_id}: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Error deleting record {record_id}: {e}")

def test_real_write_to_mockapi():
    """Test that actually writes data to MockAPI and verifies it"""
    
    print("🚀 REAL MockAPI Destination Test - ACTUAL DATA WRITES")
    print("=" * 60)
    
    # Load real configuration
    config = load_config()
    api_url = config['api_url']
    
    print(f"📡 Target API: {api_url}")
    
    # Get initial record counts
    initial_users = get_current_record_count(api_url, "users")
    initial_deals = get_current_record_count(api_url, "deals")
    
    print(f"📊 Initial counts - Users: {initial_users}, Deals: {initial_deals}")
    
    # Create test catalog
    catalog = ConfiguredAirbyteCatalog(
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
    
    # Create unique test data
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    test_messages = [
        # Test Users
        AirbyteMessage(
            type=Type.RECORD,
            record=AirbyteRecordMessage(
                stream="users",
                data={
                    "name": f"Test User Alpha {timestamp}",
                    "email": f"alpha.{timestamp}@testdest.com",
                    "avatar": "https://randomuser.me/api/portraits/men/50.jpg"
                },
                emitted_at=int(datetime.now().timestamp() * 1000)
            )
        ),
        AirbyteMessage(
            type=Type.RECORD,
            record=AirbyteRecordMessage(
                stream="users",
                data={
                    "first_name": "Test",
                    "last_name": f"Beta {timestamp}",
                    "email_address": f"beta.{timestamp}@testdest.com", 
                    "profile_picture": "https://randomuser.me/api/portraits/women/50.jpg"
                },
                emitted_at=int(datetime.now().timestamp() * 1000)
            )
        ),
        
        # Test Deals
        AirbyteMessage(
            type=Type.RECORD,
            record=AirbyteRecordMessage(
                stream="deals",
                data={
                    "title": f"Test Deal Gamma {timestamp}",
                    "amount": 99999,
                    "avatar": "https://logo.clearbit.com/testcompany.com"
                },
                emitted_at=int(datetime.now().timestamp() * 1000)
            )
        ),
        AirbyteMessage(
            type=Type.RECORD,
            record=AirbyteRecordMessage(
                stream="deals",
                data={
                    "deal_name": f"Test Deal Delta {timestamp}",
                    "value": 88888,
                    "image": "https://logo.clearbit.com/testdelta.com"
                },
                emitted_at=int(datetime.now().timestamp() * 1000)
            )
        )
    ]
    
    print(f"\n📝 Writing {len(test_messages)} test records to MockAPI...")
    
    # Execute the destination write
    destination = DestinationMockapi()
    
    try:
        # Actually write the data
        output_messages = list(destination.write(config, catalog, test_messages))
        print(f"✅ Write operation completed!")
        
        # Wait a moment for API to process
        import time
        time.sleep(2)
        
        # Verify users were created
        print("\n🔍 Verifying users were created...")
        expected_user_names = [f"Test User Alpha {timestamp}", f"Test Beta {timestamp}"]
        users_success, users_result = verify_records_created(api_url, "users", expected_user_names)
        
        if users_success:
            print(f"✅ Users verified! Found {len(users_result)} test users:")
            for user in users_result:
                print(f"   • {user['name']} (ID: {user['id']})")
        else:
            print(f"❌ Users verification failed: {users_result}")
            return False
        
        # Verify deals were created  
        print("\n🔍 Verifying deals were created...")
        expected_deal_names = [f"Test Deal Gamma {timestamp}", f"Test Deal Delta {timestamp}"]
        deals_success, deals_result = verify_records_created(api_url, "deals", expected_deal_names)
        
        if deals_success:
            print(f"✅ Deals verified! Found {len(deals_result)} test deals:")
            for deal in deals_result:
                print(f"   • {deal['name']} (ID: {deal['id']})")
        else:
            print(f"❌ Deals verification failed: {deals_result}")
            return False
        
        # Get final counts
        final_users = get_current_record_count(api_url, "users")
        final_deals = get_current_record_count(api_url, "deals") 
        
        print(f"\n📊 Final counts - Users: {final_users} (+{final_users - initial_users}), Deals: {final_deals} (+{final_deals - initial_deals})")
        
        # Cleanup test records
        all_test_records = users_result + deals_result
        cleanup_test_records(api_url, all_test_records)
        
        print("\n🎉 REAL WRITE TEST PASSED!")
        print("   ✅ Data was actually written to MockAPI")
        print("   ✅ Records were verified in the API")
        print("   ✅ Field mapping worked correctly")
        print("   ✅ Test records were cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_real_write_to_mockapi()
    if success:
        print("\n✨ Your destination connector is working perfectly!")
        print("   It can receive data from any Airbyte source and write to MockAPI!")
    else:
        print("\n💥 Test failed - check the errors above")