#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock, patch

import pytest
from source_couchbase.streams import CouchbaseStream
from source_couchbase.queries import get_documents_query

@pytest.fixture
def mock_cluster():
    return MagicMock()

def test_couchbase_stream_initialization(mock_cluster):
    stream = CouchbaseStream(mock_cluster, "test_bucket", "test_scope", "test_collection")
    assert stream.cluster == mock_cluster
    assert stream.bucket == "test_bucket"
    assert stream.scope == "test_scope"
    assert stream.collection == "test_collection"
    assert stream.name == "test_bucket.test_scope.test_collection"

def test_couchbase_stream_primary_key():
    stream = CouchbaseStream(MagicMock(), "test_bucket", "test_scope", "test_collection")
    assert stream.primary_key == "_id"

def test_couchbase_stream_read_records(mock_cluster):
    mock_cluster.query.return_value = [
        {"_id": "doc1", "key": "value1"},
        {"_id": "doc2", "key": "value2"}
    ]
    
    stream = CouchbaseStream(mock_cluster, "test_bucket", "test_scope", "test_collection")
    records = list(stream.read_records(sync_mode=None))
    
    assert len(records) == 2
    assert records[0]["_id"] == "doc1"
    assert records[0]["content"] == {"key": "value1"}
    assert records[1]["_id"] == "doc2"
    assert records[1]["content"] == {"key": "value2"}
    
    mock_cluster.query.assert_called_once_with(get_documents_query("test_bucket", "test_scope", "test_collection"))

def test_couchbase_stream_json_schema():
    stream = CouchbaseStream(MagicMock(), "test_bucket", "test_scope", "test_collection")
    schema = stream.get_json_schema()
    assert isinstance(schema, dict)
    assert "properties" in schema
    assert "_id" in schema["properties"]
    assert "content" in schema["properties"]

def test_couchbase_stream_process_row():
    stream = CouchbaseStream(MagicMock(), "test_bucket", "test_scope", "test_collection")
    row = {"_id": "doc1", "key1": "value1", "key2": "value2"}
    processed_row = stream._process_row(row)
    assert processed_row == {
        "_id": "doc1",
        "content": {"key1": "value1", "key2": "value2"}
    }
