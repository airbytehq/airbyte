# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from pymilvus import MilvusClient, __version__


print(f"Current PyMilvus version: {__version__}")
print("Milvus Lite support confirmed" if hasattr(MilvusClient, "from_local") else "Milvus Lite not found")
