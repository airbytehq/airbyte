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
    return IncrementalCouchbaseStream(mock_cluster, "test_bucket", "test_scope", "test_collection")

def test_cursor_field(incremental_stream):
    assert incremental_stream.cursor_field == "_ab_cdc_updated_at", "Cursor field is not '_ab_cdc_updated_at'"

def test_get_updated_state(incremental_stream):
    current_stream_state = {"_ab_cdc_updated_at": 1640995200000}  # 2022-01-01T00:00:00Z
    latest_record = {"_ab_cdc_updated_at": 1641081600000}  # 2022-01-02T00:00:00Z
    
    updated_state = incremental_stream.get_updated_state(current_stream_state, latest_record)
    assert updated_state == {"_ab_cdc_updated_at": 1641081600000}, "Updated state is incorrect"

def test_stream_slices(incremental_stream):
    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": ["_ab_cdc_updated_at"], "stream_state": {}}
    stream_slices = incremental_stream.stream_slices(**inputs)
    assert stream_slices == [None], "Stream slices are incorrect"

def test_supports_incremental(incremental_stream):
    assert incremental_stream.supports_incremental, "Stream does not support incremental"

def test_source_defined_cursor(incremental_stream):
    assert incremental_stream.source_defined_cursor, "Source defined cursor is incorrect"

def test_read_records_incremental(incremental_stream, mock_cluster):
    mock_cluster.query.return_value = [
        {"_id": "doc1", "_ab_cdc_updated_at": 1641081600000, "key": "value"},  # 2022-01-02T00:00:00Z
        {"_id": "doc2", "_ab_cdc_updated_at": 1641168000000, "key2": "value2"}  # 2022-01-03T00:00:00Z
    ]
    
    stream_state = {"_ab_cdc_updated_at": 1640995200000}  # 2022-01-01T00:00:00Z
    records = list(incremental_stream.read_records(sync_mode=SyncMode.incremental, cursor_field="_ab_cdc_updated_at", stream_slice=None, stream_state=stream_state))
    
    assert len(records) == 2, "Number of records is incorrect"
    assert records[0]["_ab_cdc_updated_at"] == 1641081600000, "First record _ab_cdc_updated_at is incorrect"
    assert records[1]["_ab_cdc_updated_at"] == 1641168000000, "Second record _ab_cdc_updated_at is incorrect"
    
    # Check if the query includes the incremental filter
    mock_cluster.query.assert_called_once()
    query_args = mock_cluster.query.call_args[0][0]
    assert "WHERE meta().xattrs.`$document`.last_modified > 1640995200000" in query_args
    assert "ORDER BY meta().xattrs.`$document`.last_modified ASC" in query_args

def test_get_json_schema(incremental_stream):
    schema = incremental_stream.get_json_schema()
    assert "_ab_cdc_updated_at" in schema["properties"], "_ab_cdc_updated_at is missing from the schema"
    assert schema["properties"]["_ab_cdc_updated_at"]["type"] == "number", "_ab_cdc_updated_at should be of type number"

def test_process_row(incremental_stream):
    row = {
        "_id": "doc1",
        "_ab_cdc_updated_at": 1641081600000,
        "key": "value"
    }
    processed_row = incremental_stream._process_row(row)
    assert processed_row == {
        "_id": "doc1",
        "_ab_cdc_updated_at": 1641081600000,
        "content": {"key": "value"}
    }, "Row processing is incorrect"
