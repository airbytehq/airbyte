# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
from __future__ import annotations

from unittest.mock import Mock, patch
import pytest
from destination_couchbase.destination import DestinationCouchbase
from couchbase.exceptions import CollectionAlreadyExistsException

from airbyte_cdk.models import AirbyteMessage, AirbyteRecordMessage, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, DestinationSyncMode, Status, Type, AirbyteStream, SyncMode, AirbyteStateMessage

@pytest.fixture
def config():
    return {
        "connection_string": "couchbase://localhost",
        "username": "test_user",
        "password": "test_password",
        "bucket": "test_bucket",
        "scope": "test_scope"
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
    mock_bucket = Mock()
    mock_scope = Mock()
    mock_cluster.return_value.bucket.return_value = mock_bucket
    mock_bucket.scope.return_value = mock_scope
    mock_scope.create_collection.return_value = None
    mock_scope.drop_collection.return_value = None

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
    mock_scope = Mock()
    mock_collection = Mock()
    mock_cluster.return_value.bucket.return_value = mock_bucket
    mock_bucket.scope.return_value = mock_scope
    mock_scope.collection.side_effect = [Exception, mock_collection]  # First call raises exception, second returns mock_collection
    mock_scope.create_collection.return_value = None

    messages = [
        AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream="test_stream", data={"id": 1}, emitted_at=1)),
        AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(data={"state": "test_state"}))
    ]

    destination = DestinationCouchbase()
    list(destination.write(config, configured_catalog, messages))

    # Check if _clear_collection was called for overwrite mode
    mock_cluster.return_value.query.assert_called_once()

    # Check if collection was created
    mock_scope.create_collection.assert_called_once_with("test_stream")

    # Check if upsert_multi was called for writing records
    mock_collection.upsert_multi.assert_called_once()

@patch("destination_couchbase.destination.Cluster")
def test_write_buffer_flush(mock_cluster, config, configured_catalog):
    mock_bucket = Mock()
    mock_scope = Mock()
    mock_collection = Mock()
    mock_cluster.return_value.bucket.return_value = mock_bucket
    mock_bucket.scope.return_value = mock_scope
    mock_scope.collection.side_effect = [Exception, mock_collection]  # First call raises exception, second returns mock_collection
    mock_scope.create_collection.return_value = None

    messages = [AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream="test_stream", data={"id": i}, emitted_at=1)) for i in range(1001)]
    messages.append(AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(data={"state": "test_state"})))

    destination = DestinationCouchbase()
    list(destination.write(config, configured_catalog, messages))

    # Check if upsert_multi was called twice (once for the first 1000 records, once for the remaining)
    assert mock_collection.upsert_multi.call_count == 2

@patch("destination_couchbase.destination.Cluster")
def test_write_multiple_streams(mock_cluster, config):
    mock_bucket = Mock()
    mock_scope = Mock()
    mock_collection1 = Mock()
    mock_collection2 = Mock()
    mock_cluster.return_value.bucket.return_value = mock_bucket
    mock_bucket.scope.return_value = mock_scope
    mock_scope.collection.side_effect = [Exception, mock_collection1, Exception, mock_collection2]
    mock_scope.create_collection.return_value = None

    configured_catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(name="stream1", json_schema={}, supported_sync_modes=[SyncMode.full_refresh]),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.overwrite
            ),
            ConfiguredAirbyteStream(
                stream=AirbyteStream(name="stream2", json_schema={}, supported_sync_modes=[SyncMode.full_refresh]),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.overwrite
            )
        ]
    )

    messages = [
        AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream="stream1", data={"id": 1}, emitted_at=1)),
        AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream="stream2", data={"id": 2}, emitted_at=2)),
        AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(data={"state": "test_state"}))
    ]

    destination = DestinationCouchbase()
    list(destination.write(config, configured_catalog, messages))

    # Check if collections were created for both streams
    assert mock_scope.create_collection.call_count == 2
    mock_scope.create_collection.assert_any_call("stream1")
    mock_scope.create_collection.assert_any_call("stream2")

    # Check if upsert_multi was called for both collections
    mock_collection1.upsert_multi.assert_called_once()
    mock_collection2.upsert_multi.assert_called_once()

if __name__ == "__main__":
    pytest.main()
