# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import os
import shutil

from pymilvus import MilvusClient, connections


def test_milvus_local():
    print("Testing Milvus Local functionality...")

    # Create a test database directory
    db_path = "./milvus_test_db"
    if os.path.exists(db_path):
        shutil.rmtree(db_path)
    os.makedirs(db_path)

    try:
        print("\nTesting local connection...")
        connections.connect(alias="default", uri=f"{db_path}/milvus.db", user="", password="", db_name="")
        print("✓ Successfully connected to local Milvus")

        # Try to create a collection
        from pymilvus import Collection, CollectionSchema, DataType, FieldSchema

        print("\nTesting collection creation...")
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=4),
        ]
        schema = CollectionSchema(fields=fields, description="Test collection")
        collection = Collection(name="test_collection", schema=schema)
        print("✓ Successfully created collection")

        # Insert some test data
        print("\nTesting data insertion...")
        entities = [{"vector": [1.0, 2.0, 3.0, 4.0]}, {"vector": [5.0, 6.0, 7.0, 8.0]}]
        collection.insert(entities)
        print("✓ Successfully inserted data")

        # Query the data
        print("\nTesting data retrieval...")
        collection.flush()
        results = collection.query(expr="id >= 0")
        print(f"✓ Successfully retrieved {len(results)} records")

    except Exception as e:
        print(f"× Error: {str(e)}")
        raise
    finally:
        # Clean up
        try:
            connections.disconnect("default")
        except:
            pass
        if os.path.exists(db_path):
            shutil.rmtree(db_path)
        print("\nTest completed and cleaned up")


if __name__ == "__main__":
    test_milvus_local()
