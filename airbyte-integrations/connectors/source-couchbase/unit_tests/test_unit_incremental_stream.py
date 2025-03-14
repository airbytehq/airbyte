# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from unittest.mock import MagicMock

import pytest
from source_couchbase.streams import DocumentStream

from airbyte_cdk.models import AirbyteRecordMessage, SyncMode


@pytest.fixture
def mock_cluster():
    return MagicMock()


@pytest.fixture
def document_stream(mock_cluster):
    return DocumentStream(mock_cluster, "test_bucket", "test_scope", "test_collection")


def test_cursor_field(document_stream):
    assert document_stream.cursor_field == "_ab_cdc_updated_at"


def test_get_updated_state(document_stream):
    current_state = {"_ab_cdc_updated_at": 100}
    latest_record = AirbyteRecordMessage(stream="test", data={"_ab_cdc_updated_at": 200}, emitted_at=1234)

    new_state = document_stream.get_updated_state(current_state, latest_record)
    assert new_state == {"_ab_cdc_updated_at": 200}

    # Test when latest record has lower cursor value
    latest_record = AirbyteRecordMessage(stream="test", data={"_ab_cdc_updated_at": 50}, emitted_at=1234)
    new_state = document_stream.get_updated_state(current_state, latest_record)
    assert new_state == {"_ab_cdc_updated_at": 100}


def test_read_records_full_refresh(document_stream, mock_cluster):
    mock_cluster.query.return_value = [
        {"_id": "doc1", "_ab_cdc_updated_at": 100, "test_collection": {"key": "value1"}},
        {"_id": "doc2", "_ab_cdc_updated_at": 200, "test_collection": {"key": "value2"}},
    ]

    records = list(document_stream.read_records(sync_mode=SyncMode.full_refresh))
    assert len(records) == 2
    assert records[0].record.data == {"_id": "doc1", "_ab_cdc_updated_at": 100, "test_collection": {"key": "value1"}}
    assert records[1].record.data == {"_id": "doc2", "_ab_cdc_updated_at": 200, "test_collection": {"key": "value2"}}


def test_read_records_incremental(document_stream, mock_cluster):
    mock_cluster.query.return_value = [
        {"_id": "doc2", "_ab_cdc_updated_at": 200, "test_collection": {"key": "value2"}},
        {"_id": "doc3", "_ab_cdc_updated_at": 300, "test_collection": {"key": "value3"}},
    ]

    stream_state = {"_ab_cdc_updated_at": 100}
    records = list(document_stream.read_records(sync_mode=SyncMode.incremental, stream_state=stream_state))

    assert len(records) == 2
    assert records[0].record.data == {"_id": "doc2", "_ab_cdc_updated_at": 200, "test_collection": {"key": "value2"}}
    assert records[1].record.data == {"_id": "doc3", "_ab_cdc_updated_at": 300, "test_collection": {"key": "value3"}}
    assert document_stream.state == {"_ab_cdc_updated_at": 300}


def test_get_json_schema(document_stream):
    schema = document_stream.get_json_schema()
    assert schema["type"] == "object"
    assert "_id" in schema["properties"]
    assert "_ab_cdc_updated_at" in schema["properties"]
    assert "test_collection" in schema["properties"]
