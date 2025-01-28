from pymilvus import __version__, MilvusClient

print(f"Current PyMilvus version: {__version__}")
print("Milvus Lite support confirmed" if hasattr(MilvusClient, "from_local") else "Milvus Lite not found")
