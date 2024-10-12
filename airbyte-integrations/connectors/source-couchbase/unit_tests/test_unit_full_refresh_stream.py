#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock, patch

import pytest
from airbyte_cdk.models import SyncMode
from source_couchbase.streams import DocumentStream
from source_couchbase.queries import get_documents_query

@pytest.fixture
def mock_cluster():
    return MagicMock()

def test_document_stream_initialization(mock_cluster):
    stream = DocumentStream(mock_cluster, "test_bucket", "test_scope", "test_collection", cursor_field="_ab_cdc_updated_at")
    assert stream.cluster == mock_cluster
    assert stream.bucket == "test_bucket"
    assert stream.scope == "test_scope"
    assert stream.collection == "test_collection"
    assert stream.name == "test_bucket.test_scope.test_collection"
    assert stream.cursor_field == "_ab_cdc_updated_at"

def test_document_stream_primary_key():
    stream = DocumentStream(MagicMock(), "test_bucket", "test_scope", "test_collection", cursor_field="_ab_cdc_updated_at")
    assert stream.primary_key == "_id"

def test_document_stream_read_records(mock_cluster):
    mock_cluster.query.return_value = [
        {"_id": "doc1", "test_collection": {"key": "value1"}},
        {"_id": "doc2", "test_collection": {"key": "value2"}}
    ]
    
    stream = DocumentStream(mock_cluster, "test_bucket", "test_scope", "test_collection", cursor_field="_ab_cdc_updated_at")
    records = list(stream.read_records(sync_mode=SyncMode.full_refresh))
    
    assert len(records) == 2
    assert records[0] == {"_id": "doc1", "test_collection": {"key": "value1"}}
    assert records[1] == {"_id": "doc2", "test_collection": {"key": "value2"}}
    
    mock_cluster.query.assert_called_once_with(get_documents_query("test_bucket", "test_scope", "test_collection"))

def test_document_stream_json_schema():
    stream = DocumentStream(MagicMock(), "test_bucket", "test_scope", "test_collection", cursor_field="_ab_cdc_updated_at")
    schema = stream.get_json_schema()
    assert isinstance(schema, dict)
    assert "properties" in schema
    assert "_id" in schema["properties"]
    assert "_ab_cdc_updated_at" in schema["properties"]
    assert "test_collection" in schema["properties"]
    assert schema["properties"]["test_collection"]["type"] == "object"
    assert schema["properties"]["test_collection"]["additionalProperties"] == True
