# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

try:
    from pymilvus import MilvusClient

    print("Trying standard MilvusClient import...")
    print(f"Has from_local: {hasattr(MilvusClient, 'from_local')}")
except Exception as e1:
    print(f"Standard import error: {e1}")

try:
    from pymilvus.client.lite import MilvusLite

    print("\nTrying direct MilvusLite import...")
    print("MilvusLite import successful")
except Exception as e2:
    print(f"MilvusLite import error: {e2}")

# Try to create a lite instance
try:
    from pymilvus import connections

    print("\nTrying to create Milvus Lite connection...")
    connections.connect(uri="lite://test.db")
    print("Successfully created Milvus Lite connection")
except Exception as e3:
    print(f"Connection error: {e3}")
