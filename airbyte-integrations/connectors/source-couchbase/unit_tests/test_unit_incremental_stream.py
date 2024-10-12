#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
from airbyte_cdk.models import SyncMode
from source_couchbase.streams import DocumentStream


@pytest.fixture
def mock_cluster():
    return MagicMock()

@pytest.fixture
def document_stream(mock_cluster):
    return DocumentStream(mock_cluster, "test_bucket", "test_scope", "test_collection", cursor_field="_ab_cdc_updated_at")

def test_cursor_field(document_stream):
    assert document_stream.cursor_field == "_ab_cdc_updated_at", "Cursor field is not '_ab_cdc_updated_at'"

def test_get_updated_state(document_stream):
    current_stream_state = {"_ab_cdc_updated_at": 1640995200000}  # 2022-01-01T00:00:00Z
    latest_record = {"_ab_cdc_updated_at": 1641081600000}  # 2022-01-02T00:00:00Z
    
    updated_state = document_stream.get_updated_state(current_stream_state, latest_record)
    assert updated_state == {"_ab_cdc_updated_at": 1641081600000}, "Updated state is incorrect"

def test_read_records_full_refresh(document_stream, mock_cluster):
    mock_cluster.query.return_value = [
        {"_id": "doc1", "_ab_cdc_updated_at": 1641081600000, "test_collection": {"key": "value"}},
        {"_id": "doc2", "_ab_cdc_updated_at": 1641168000000, "test_collection": {"key2": "value2"}}
    ]
    
    records = list(document_stream.read_records(sync_mode=SyncMode.full_refresh))
    
    assert len(records) == 2, "Number of records is incorrect"
    assert records[0]["_ab_cdc_updated_at"] == 1641081600000, "First record _ab_cdc_updated_at is incorrect"
    assert records[1]["_ab_cdc_updated_at"] == 1641168000000, "Second record _ab_cdc_updated_at is incorrect"
    
    mock_cluster.query.assert_called_once()
    query_args = mock_cluster.query.call_args[0][0]
    assert "WHERE meta().xattrs.`$document`.last_modified > 1640995200000" not in query_args
    assert "ORDER BY meta().xattrs.`$document`.last_modified ASC" not in query_args

def test_read_records_incremental(document_stream, mock_cluster):
    mock_cluster.query.return_value = [
        {"_id": "doc1", "_ab_cdc_updated_at": 1641081600000, "test_collection": {"key": "value"}},
        {"_id": "doc2", "_ab_cdc_updated_at": 1641168000000, "test_collection": {"key2": "value2"}}
    ]
    
    stream_state = {"_ab_cdc_updated_at": 1640995200000}  # 2022-01-01T00:00:00Z
    records = list(document_stream.read_records(sync_mode=SyncMode.incremental, stream_state=stream_state))
    
    assert len(records) == 2, "Number of records is incorrect"
    assert records[0]["_ab_cdc_updated_at"] == 1641081600000, "First record _ab_cdc_updated_at is incorrect"
    assert records[1]["_ab_cdc_updated_at"] == 1641168000000, "Second record _ab_cdc_updated_at is incorrect"
    
    mock_cluster.query.assert_called_once()
    query_args = mock_cluster.query.call_args[0][0]
    assert "WHERE meta().xattrs.`$document`.last_modified > 1640995200000" in query_args
    assert "ORDER BY meta().xattrs.`$document`.last_modified ASC" in query_args

def test_get_json_schema(document_stream):
    schema = document_stream.get_json_schema()
    assert "_ab_cdc_updated_at" in schema["properties"], "_ab_cdc_updated_at is missing from the schema"
    assert schema["properties"]["_ab_cdc_updated_at"]["type"] == "integer", "_ab_cdc_updated_at should be of type integer"
    assert "test_collection" in schema["properties"], "test_collection is missing from the schema"
    assert schema["properties"]["test_collection"]["type"] == "object", "test_collection should be of type object"
    assert schema["properties"]["test_collection"]["additionalProperties"] == True, "test_collection should allow additional properties"
