#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock
from airbyte_cdk.models import SyncMode
import pytest
from source_couchbase.streams import Documents

@pytest.fixture
def mock_cluster():
    return MagicMock()

@pytest.fixture
def documents_stream(mock_cluster):
    return Documents(mock_cluster)

def test_cursor_field(documents_stream):
    assert documents_stream.cursor_field == "metadata.cas"

def test_get_updated_state(documents_stream):
    current_stream_state = {"metadata.cas": "1000"}
    latest_record = {"metadata": {"cas": "2000"}}
    
    updated_state = documents_stream.get_updated_state(current_stream_state, latest_record)
    assert updated_state == {"metadata.cas": "2000"}

def test_stream_slices(documents_stream):
    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": ["metadata", "cas"], "stream_state": {}}
    stream_slices = documents_stream.stream_slices(**inputs)
    assert stream_slices == [None]

def test_supports_incremental(documents_stream):
    assert documents_stream.supports_incremental

def test_source_defined_cursor(documents_stream):
    assert documents_stream.source_defined_cursor

def test_stream_checkpoint_interval(documents_stream):
    assert documents_stream.state_checkpoint_interval == 1000  # Assuming we set this value in the Documents stream

def test_read_records_incremental(documents_stream, mock_cluster):
    mock_cluster.query.side_effect = [
        [{"name": "bucket1"}],  # Mocking buckets_list_query result
        [  # Mocking documents_query result
            {"id": "doc1", "bucket": "bucket1", "scope": "scope1", "collection": "collection1", "content": {"key": "value"}, "expiration": 0, "flags": 0, "cas": "2000"},
            {"id": "doc2", "bucket": "bucket1", "scope": "scope1", "collection": "collection1", "content": {"key2": "value2"}, "expiration": 0, "flags": 0, "cas": "3000"}
        ]
    ]
    
    mock_bucket = MagicMock()
    mock_scope = MagicMock()
    mock_collection = MagicMock()
    
    mock_bucket.name = "bucket1"
    mock_scope.name = "scope1"
    mock_collection.name = "collection1"
    
    mock_bucket.collections.return_value.get_all_scopes.return_value = [mock_scope]
    mock_scope.collections = [mock_collection]
    mock_cluster.bucket.return_value = mock_bucket
    
    stream_state = {"metadata.cas": "1000"}
    records = list(documents_stream.read_records(sync_mode=SyncMode.incremental, cursor_field="metadata.cas", stream_slice=None, stream_state=stream_state))
    
    assert len(records) == 2
    assert records[0]["metadata"]["cas"] == "2000"
    assert records[1]["metadata"]["cas"] == "3000"
    
    # Check if the query includes the incremental filter
    expected_query = documents_stream.get_documents_query().format("bucket1", "scope1", "collection1")
    expected_query += " WHERE META(d).cas > 1000"
    mock_cluster.query.assert_any_call(expected_query)
