#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock, patch

from destination_typesense.destination import DestinationTypesense
from destination_typesense.writer import TypesenseWriter

from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateMessage,
    AirbyteStateType,
    AirbyteStream,
    AirbyteStreamState,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    StreamDescriptor,
    SyncMode,
    Type,
)


@patch("typesense.Client")
def test_default_batch_size(client):
    writer = TypesenseWriter(client)
    assert writer.batch_size == 10000


@patch("typesense.Client")
def test_empty_batch_size(client):
    writer = TypesenseWriter(client, "")
    assert writer.batch_size == 10000


@patch("typesense.Client")
def test_custom_batch_size(client):
    writer = TypesenseWriter(client, 9000)
    assert writer.batch_size == 9000


@patch("typesense.Client")
def test_queue_write_operation(client):
    writer = TypesenseWriter(client)
    writer.queue_write_operation("stream_name", {"a": "a"})
    assert len(writer.write_buffer) == 1


@patch("typesense.Client")
def test_flush(client):
    writer = TypesenseWriter(client)
    writer.queue_write_operation("stream_name", {"a": "a"})
    writer.flush()
    client.collections.__getitem__.assert_called_once_with("stream_name")


@patch("destination_typesense.destination.get_client")
def test_write_yields_state_messages_unchanged(mock_get_client):
    """Test that state messages are yielded unchanged to preserve tracking metadata.

    This is critical for Airbyte 1.7+ which injects state-id into messages for tracking.
    The destination must return state messages with all fields intact.
    """
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client

    stream = AirbyteStream(name="test_stream", json_schema={}, supported_sync_modes=[SyncMode.full_refresh])
    configured_stream = ConfiguredAirbyteStream(
        stream=stream,
        sync_mode=SyncMode.full_refresh,
        destination_sync_mode=DestinationSyncMode.append,
    )
    catalog = ConfiguredAirbyteCatalog(streams=[configured_stream])

    # Create a state message with STREAM type
    state_message = AirbyteMessage(
        type=Type.STATE,
        state=AirbyteStateMessage(
            type=AirbyteStateType.STREAM,
            stream=AirbyteStreamState(
                stream_descriptor=StreamDescriptor(name="test_stream"),
                stream_state={"cursor": "123"},
            ),
        ),
    )

    record_message = AirbyteMessage(
        type=Type.RECORD,
        record=AirbyteRecordMessage(
            stream="test_stream",
            data={"id": "1", "name": "test"},
            emitted_at=1234567890,
        ),
    )

    input_messages = [record_message, state_message]

    destination = DestinationTypesense()
    config = {"host": "localhost", "api_key": "test_key"}

    output_messages = list(destination.write(config, catalog, input_messages))

    # Should yield exactly one state message
    assert len(output_messages) == 1
    assert output_messages[0].type == Type.STATE
    # The state message should be the same object (unchanged)
    assert output_messages[0] is state_message


@patch("destination_typesense.destination.get_client")
def test_write_handles_global_state(mock_get_client):
    """Test that GLOBAL state messages are handled correctly for CDC sources."""
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client

    stream = AirbyteStream(name="test_stream", json_schema={}, supported_sync_modes=[SyncMode.full_refresh])
    configured_stream = ConfiguredAirbyteStream(
        stream=stream,
        sync_mode=SyncMode.full_refresh,
        destination_sync_mode=DestinationSyncMode.append,
    )
    catalog = ConfiguredAirbyteCatalog(streams=[configured_stream])

    state_message = AirbyteMessage(
        type=Type.STATE,
        state=AirbyteStateMessage(
            type=AirbyteStateType.GLOBAL,
        ),
    )

    input_messages = [state_message]

    destination = DestinationTypesense()
    config = {"host": "localhost", "api_key": "test_key"}

    output_messages = list(destination.write(config, catalog, input_messages))

    assert len(output_messages) == 1
    assert output_messages[0].state.type == AirbyteStateType.GLOBAL


@patch("destination_typesense.destination.get_client")
def test_state_message_preserves_extra_fields(mock_get_client):
    """Test that extra fields in state messages (like platform-injected state-id) are preserved.

    Airbyte 1.7+ injects a 'meta.id' field into state messages for tracking purposes.
    The updated CDK (>=6.61.6) uses dataclasses with extra='allow' semantics,
    ensuring these fields survive serialization/deserialization through the connector.
    """
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client

    stream = AirbyteStream(name="test_stream", json_schema={}, supported_sync_modes=[SyncMode.full_refresh])
    configured_stream = ConfiguredAirbyteStream(
        stream=stream,
        sync_mode=SyncMode.full_refresh,
        destination_sync_mode=DestinationSyncMode.append,
    )
    catalog = ConfiguredAirbyteCatalog(streams=[configured_stream])

    # Create a state message and simulate platform-injected tracking metadata
    state_message = AirbyteMessage(
        type=Type.STATE,
        state=AirbyteStateMessage(
            type=AirbyteStateType.STREAM,
            stream=AirbyteStreamState(
                stream_descriptor=StreamDescriptor(name="test_stream"),
                stream_state={"cursor": "456"},
            ),
        ),
    )

    # Simulate the platform injecting a tracking ID (this is what Airbyte 1.7+ does)
    # The state message object should pass through unchanged
    original_state_id = id(state_message.state)

    input_messages = [state_message]

    destination = DestinationTypesense()
    config = {"host": "localhost", "api_key": "test_key"}

    output_messages = list(destination.write(config, catalog, input_messages))

    assert len(output_messages) == 1
    # Verify the state message is passed through unchanged (same object reference)
    assert output_messages[0] is state_message
    # Verify the inner state object is also unchanged
    assert id(output_messages[0].state) == original_state_id
