#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
from airbyte_cdk.models import SyncMode
from source_couchbase.streams import IncrementalCouchbaseStream


@pytest.fixture
def mock_cluster():
    return MagicMock()

@pytest.fixture
def incremental_stream(mock_cluster):
    return IncrementalCouchbaseStream(mock_cluster, "test_bucket", "test_scope", "test_collection", "updated_at")

def test_cursor_field(incremental_stream):
    assert incremental_stream.cursor_field == "updated_at", "Cursor field is not 'updated_at'"

def test_get_updated_state(incremental_stream):
    current_stream_state = {"updated_at": "2023-01-01T00:00:00Z"}
    latest_record = {"content": {"updated_at": "2023-01-02T00:00:00Z"}}
    
    updated_state = incremental_stream.get_updated_state(current_stream_state, latest_record)
    assert updated_state == {"updated_at": "2023-01-02T00:00:00Z"}, "Updated state is incorrect"

def test_stream_slices(incremental_stream):
    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": ["updated_at"], "stream_state": {}}
    stream_slices = incremental_stream.stream_slices(**inputs)
    assert stream_slices == [None], "Stream slices are incorrect"

def test_supports_incremental(incremental_stream):
    assert incremental_stream.supports_incremental, "Stream does not support incremental"

def test_source_defined_cursor(incremental_stream):
    assert incremental_stream.source_defined_cursor, "Source defined cursor is incorrect"

def test_read_records_incremental(incremental_stream, mock_cluster):
    mock_cluster.query.return_value = [
        {"id": "doc1", "content": {"key": "value", "updated_at": "2023-01-02T00:00:00Z"}},
        {"id": "doc2", "content": {"key2": "value2", "updated_at": "2023-01-03T00:00:00Z"}}
    ]
    
    stream_state = {"updated_at": "2023-01-01T00:00:00Z"}
    records = list(incremental_stream.read_records(sync_mode=SyncMode.incremental, cursor_field="updated_at", stream_slice=None, stream_state=stream_state))
    
    assert len(records) == 2, "Number of records is incorrect"
    assert records[0]["content"]["updated_at"] == "2023-01-02T00:00:00Z", "First record updated_at is incorrect"
    assert records[1]["content"]["updated_at"] == "2023-01-03T00:00:00Z", "Second record updated_at is incorrect"
    
    # Check if the query includes the incremental filter
    mock_cluster.query.assert_called_once()
    query_args = mock_cluster.query.call_args[0][0]
    assert "WHERE updated_at > '2023-01-01T00:00:00Z'" in query_args
    assert "ORDER BY updated_at ASC" in query_args
