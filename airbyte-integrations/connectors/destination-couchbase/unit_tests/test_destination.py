# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
from __future__ import annotations

from unittest.mock import Mock, patch
import pytest
from destination_couchbase.destination import DestinationCouchbase

from airbyte_cdk.models import AirbyteMessage, AirbyteRecordMessage, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, DestinationSyncMode, Status, Type, AirbyteStream, SyncMode, AirbyteStateMessage

@pytest.fixture
def config():
    return {
        "connection_string": "couchbase://localhost",
        "username": "test_user",
        "password": "test_password",
        "bucket": "test_bucket"
    }

@pytest.fixture
def configured_catalog():
    return ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(
                    name="test_stream",
                    json_schema={},
                    supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental]
                ),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.overwrite
            )
        ]
    )

@patch("destination_couchbase.destination.Cluster")
def test_check_success(mock_cluster, config):
    mock_cluster.return_value.bucket.return_value.ping.return_value = True
    logger = Mock()
    destination = DestinationCouchbase()
    result = destination.check(logger, config)
    assert result.status == Status.SUCCEEDED

@patch("destination_couchbase.destination.Cluster")
def test_check_failure(mock_cluster, config):
    mock_cluster.side_effect = Exception("Test exception")
    logger = Mock()
    destination = DestinationCouchbase()
    result = destination.check(logger, config)
    assert result.status == Status.FAILED
    assert "Test exception" in result.message

@patch("destination_couchbase.destination.Cluster")
def test_write(mock_cluster, config, configured_catalog):
    mock_bucket = Mock()
    mock_collection = Mock()
    mock_cluster.return_value.bucket.return_value = mock_bucket
    mock_bucket.default_collection.return_value = mock_collection

    messages = [
        AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream="test_stream", data={"id": 1}, emitted_at=1)),
        AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(data={"state": "test_state"}))
    ]

    destination = DestinationCouchbase()
    list(destination.write(config, configured_catalog, messages))

    # Check if _clear_collection was called for overwrite mode
    mock_bucket.cluster.query.assert_called_once()

    # Check if insert_multi was called for writing records
    mock_collection.insert_multi.assert_called_once()

@patch("destination_couchbase.destination.Cluster")
def test_write_buffer_flush(mock_cluster, config, configured_catalog):
    mock_bucket = Mock()
    mock_collection = Mock()
    mock_cluster.return_value.bucket.return_value = mock_bucket
    mock_bucket.default_collection.return_value = mock_collection

    messages = [AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream="test_stream", data={"id": i}, emitted_at=1)) for i in range(1001)]
    messages.append(AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(data={"state": "test_state"})))

    destination = DestinationCouchbase()
    list(destination.write(config, configured_catalog, messages))

    # Check if insert_multi was called twice (once for the first 1000 records, once for the remaining)
    assert mock_collection.insert_multi.call_count == 2

if __name__ == "__main__":
    pytest.main()
