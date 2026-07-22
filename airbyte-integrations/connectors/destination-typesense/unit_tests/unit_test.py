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


def test_state_message_serialization_preserves_platform_id():
    """Test that AirbyteStateMessage serialization preserves platform-injected 'id' field.

    This is a regression test for the "State message does not contain id" error.

    The Airbyte platform (v1.7+) attaches an 'id' field to state messages via
    additionalProperties for tracking purposes. The Python CDK must preserve this
    field through the serialization/deserialization round-trip.

    Without the cdk_patches fix, this test would fail because the standard
    AirbyteStateMessage dataclass drops unknown fields during deserialization.
    """
    import json

    from airbyte_cdk.models.airbyte_protocol_serializers import (
        AirbyteMessageSerializer,
        AirbyteStateMessageSerializer,
    )

    # Simulate JSON input from platform with injected 'id' field
    platform_state_json = {
        "type": "STREAM",
        "id": 12345,  # Platform-injected tracking ID
        "stream": {"stream_descriptor": {"name": "test_stream"}, "stream_state": {"cursor": "abc123"}},
        "platform_metadata": "should_also_be_preserved",  # Any extra field
    }

    # Deserialize (simulate receiving from platform)
    state_msg = AirbyteStateMessageSerializer.load(platform_state_json)

    # Serialize back (simulate sending back to platform)
    output_json = AirbyteStateMessageSerializer.dump(state_msg)

    # The 'id' field MUST be preserved - this is what the platform checks
    assert (
        "id" in output_json
    ), "Platform 'id' field was lost during serialization! This will cause 'State message does not contain id' error in Airbyte 1.7+"
    assert output_json["id"] == 12345, "Platform 'id' value was corrupted"

    # Other extra fields should also be preserved
    assert output_json.get("platform_metadata") == "should_also_be_preserved", "Additional properties were not preserved"


def test_airbyte_message_with_state_preserves_platform_id():
    """Test full AirbyteMessage round-trip preserves state.id field.

    This tests the complete message flow as it occurs in practice:
    Platform sends AirbyteMessage JSON → Connector deserializes → Connector serializes back
    """
    from airbyte_cdk.models.airbyte_protocol_serializers import AirbyteMessageSerializer

    # Full AirbyteMessage as sent by platform
    platform_message_json = {
        "type": "STATE",
        "state": {
            "type": "STREAM",
            "id": 67890,  # Platform tracking ID
            "stream": {"stream_descriptor": {"name": "users"}, "stream_state": {"updated_at": "2024-01-01"}},
        },
    }

    # Round-trip through serializer
    message = AirbyteMessageSerializer.load(platform_message_json)
    output_json = AirbyteMessageSerializer.dump(message)

    # Verify state.id is preserved
    assert "state" in output_json
    assert "id" in output_json["state"], "state.id was lost! Platform will fail with 'State message does not contain id'"
    assert output_json["state"]["id"] == 67890
