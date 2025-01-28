import os
from pymilvus import MilvusClient, connections

def test_milvus_lite():
    print("Testing Milvus Lite functionality...")
    
    # Create a test database file path
    db_path = "./test_milvus.db"
    
    try:
        # Try the new style client first
        print("\nTesting MilvusClient approach:")
        client = MilvusClient(
            uri=f"lite://{db_path}",
            token=""  # No token needed for lite
        )
        print("✓ Successfully created MilvusClient with lite:// URI")
        
    except Exception as e:
        print(f"× MilvusClient approach failed: {str(e)}")
    
    try:
        # Try the connections approach
        print("\nTesting connections approach:")
        connections.connect(
            alias="default",
            uri=f"lite://{db_path}"
        )
        print("✓ Successfully connected using connections.connect()")
        connections.disconnect("default")
        
    except Exception as e:
        print(f"× Connections approach failed: {str(e)}")
    
    # Clean up test database if it exists
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"\nCleaned up test database at {db_path}")
        except Exception as e:
            print(f"Failed to clean up test database: {str(e)}")

if __name__ == "__main__":
    test_milvus_lite()
