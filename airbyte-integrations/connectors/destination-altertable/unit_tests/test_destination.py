# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from __future__ import annotations

from unittest.mock import MagicMock, patch

from destination_altertable.destination import DestinationAltertable

from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateMessage,
    AirbyteStream,
    AirbyteStreamState,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    Status,
    StreamDescriptor,
    SyncMode,
    Type,
)


CONFIG = {
    "host": "localhost",
    "port": 15002,
    "username": "test",
    "password": "test",
    "catalog": "my_catalog",
    "schema": "main",
    "tls": False,
}

CATALOG = ConfiguredAirbyteCatalog(
    streams=[
        ConfiguredAirbyteStream(
            stream=AirbyteStream(
                name="test_table",
                json_schema={
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "name": {"type": "string"},
                    },
                },
                supported_sync_modes=[SyncMode.full_refresh],
            ),
            sync_mode=SyncMode.full_refresh,
            destination_sync_mode=DestinationSyncMode.overwrite,
        )
    ]
)


@patch("destination_altertable.destination.AltertableWriter")
def test_check_succeeds(mock_writer_class) -> None:
    mock_writer = MagicMock()
    mock_writer_class.return_value.__enter__.return_value = mock_writer

    destination = DestinationAltertable()
    result = destination.check(logger=MagicMock(), config=CONFIG)

    assert result.status == Status.SUCCEEDED
    mock_writer.test_connection.assert_called_once()


@patch("destination_altertable.destination.AltertableWriter")
def test_check_fails_on_connection_error(mock_writer_class) -> None:
    mock_writer_class.return_value.__enter__.side_effect = Exception("connection refused")

    destination = DestinationAltertable()
    result = destination.check(logger=MagicMock(), config=CONFIG)

    assert result.status == Status.FAILED
    assert "connection refused" in result.message


@patch("destination_altertable.destination.AltertableWriter")
def test_check_fails_on_test_connection_error(mock_writer_class) -> None:
    mock_writer = MagicMock()
    mock_writer.test_connection.side_effect = Exception("auth failed")
    mock_writer_class.return_value.__enter__.return_value = mock_writer

    destination = DestinationAltertable()
    result = destination.check(logger=MagicMock(), config=CONFIG)

    assert result.status == Status.FAILED
    assert "auth failed" in result.message


@patch("destination_altertable.destination.AltertableWriter")
def test_write_yields_state_messages(mock_writer_class) -> None:
    mock_writer = MagicMock()
    mock_writer_class.return_value.__enter__.return_value = mock_writer

    state_message = AirbyteMessage(
        type=Type.STATE,
        state=AirbyteStateMessage(
            stream=AirbyteStreamState(
                stream_descriptor=StreamDescriptor(name="test_table"),
            ),
        ),
    )
    record_message = AirbyteMessage(
        type=Type.RECORD,
        record=AirbyteRecordMessage(
            stream="test_table",
            data={"id": 1, "name": "Alice"},
            emitted_at=1000,
        ),
    )

    destination = DestinationAltertable()
    result = list(destination.write(CONFIG, CATALOG, [record_message, state_message]))

    assert len(result) == 1
    assert result[0].type == Type.STATE
    mock_writer.set_streams.assert_called_once_with(CATALOG)
    mock_writer.buffer_record.assert_called_once_with(record_message.record)
    mock_writer.flush.assert_called_once()


@patch("destination_altertable.destination.AltertableWriter")
def test_write_flushes_on_each_state(mock_writer_class) -> None:
    mock_writer = MagicMock()
    mock_writer_class.return_value.__enter__.return_value = mock_writer

    def make_state():
        return AirbyteMessage(
            type=Type.STATE,
            state=AirbyteStateMessage(
                stream=AirbyteStreamState(
                    stream_descriptor=StreamDescriptor(name="test_table"),
                ),
            ),
        )

    def make_record(i: int):
        return AirbyteMessage(
            type=Type.RECORD,
            record=AirbyteRecordMessage(
                stream="test_table",
                data={"id": i, "name": f"Person {i}"},
                emitted_at=1000,
            ),
        )

    messages = [make_record(1), make_state(), make_record(2), make_state()]

    destination = DestinationAltertable()
    result = list(destination.write(CONFIG, CATALOG, messages))

    assert len(result) == 2
    assert mock_writer.flush.call_count == 2
    assert mock_writer.buffer_record.call_count == 2


@patch("destination_altertable.destination.AltertableWriter")
def test_write_empty_messages(mock_writer_class) -> None:
    mock_writer = MagicMock()
    mock_writer_class.return_value.__enter__.return_value = mock_writer

    destination = DestinationAltertable()
    result = list(destination.write(CONFIG, CATALOG, []))

    assert result == []
    mock_writer.flush.assert_not_called()
