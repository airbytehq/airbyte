#!/usr/bin/env python3
"""Test script to verify Milvus Lite connection."""

import logging
import os
import shutil
import sys
import tempfile
from contextlib import contextmanager
from pymilvus import connections, utility

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_milvus_lite_connection():
    """Test basic Milvus Lite connection and operations."""
    temp_dir = tempfile.mkdtemp(prefix="milvus_lite_test_")
    db_path = os.path.join(temp_dir, "test.db")
    
    try:
        # Connect to Milvus Lite
        logger.info(f"Connecting to Milvus Lite at {db_path}")
        connections.connect(
            alias="default",
            uri=db_path,
            use_lite=True,
            timeout=30
        )
        logger.info("Successfully connected to Milvus Lite")
        
        # List connections
        conns = connections.list_connections()
        logger.info(f"Active connections: {conns}")
        
        # Check if connection is working
        assert connections.has_connection("default"), "Connection not established"
        
        # For Milvus Lite, we'll test basic collection operations instead of version check
        test_collection = "test_collection"
        
        # Create a test collection
        from pymilvus import Collection, CollectionSchema, DataType, FieldSchema
        
        if utility.has_collection(test_collection):
            utility.drop_collection(test_collection)
            
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=8)
        ]
        schema = CollectionSchema(fields=fields, enable_dynamic_field=True)
        collection = Collection(name=test_collection, schema=schema)
        
        # Create FLAT index (only supported type in Milvus Lite)
        collection.create_index(
            field_name="vector",
            index_params={"metric_type": "L2", "index_type": "FLAT"}
        )
        
        logger.info("Successfully created test collection and index")
        utility.drop_collection(test_collection)
        
        return True
        
    except Exception as e:
        logger.error(f"Connection test failed: {str(e)}")
        return False
        
    finally:
        # Clean up
        try:
            if connections.has_connection("default"):
                connections.disconnect("default")
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception as e:
            logger.warning(f"Cleanup error: {str(e)}")

if __name__ == "__main__":
    success = test_milvus_lite_connection()
    sys.exit(0 if success else 1)
