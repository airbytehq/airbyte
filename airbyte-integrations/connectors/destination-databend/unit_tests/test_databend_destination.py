#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from datetime import datetime
from typing import Dict
from unittest.mock import AsyncMock, MagicMock, call, patch

from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    SyncMode,
    Type,
)
from destination_databend.destination import DatabendClient, DestinationDatabend
from pytest import fixture


@fixture
def logger() -> MagicMock:
    return MagicMock()


@fixture
def config() -> Dict[str, str]:
    args = {
        "database": "default",
        "username": "root",
        "password": "root",
        "host": "localhost",
        "port": 8081,
        "table": "default",
    }
    return args


@fixture(name="mock_connection")
def async_connection_cursor_mock():
    connection = MagicMock()
    cursor = AsyncMock()
    connection.cursor.return_value = cursor
    return connection, cursor


@fixture
def configured_stream1() -> ConfiguredAirbyteStream:
    return ConfiguredAirbyteStream(
        stream=AirbyteStream(
            name="table1",
            json_schema={
                "type": "object",
                "properties": {"col1": {"type": "string"}, "col2": {"type": "integer"}},
            },
            supported_sync_modes=[SyncMode.incremental],
        ),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.append,
    )


@fixture
def configured_stream2() -> ConfiguredAirbyteStream:
    return ConfiguredAirbyteStream(
        stream=AirbyteStream(
            name="table2",
            json_schema={
                "type": "object",
                "properties": {"col1": {"type": "string"}, "col2": {"type": "integer"}},
            },
            supported_sync_modes=[SyncMode.incremental],
        ),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.append,
    )


@fixture
def airbyte_message1() -> AirbyteMessage:
    return AirbyteMessage(
        type=Type.RECORD,
        record=AirbyteRecordMessage(
            stream="table1",
            data={"key1": "value1", "key2": 2},
            emitted_at=int(datetime.now().timestamp()) * 1000,
        ),
    )


@fixture
def airbyte_message2() -> AirbyteMessage:
    return AirbyteMessage(
        type=Type.RECORD,
        record=AirbyteRecordMessage(
            stream="table2",
            data={"key1": "value2", "key2": 3},
            emitted_at=int(datetime.now().timestamp()) * 1000,
        ),
    )


@fixture
def airbyte_state_message() -> AirbyteMessage:
    return AirbyteMessage(type=Type.STATE)


@patch("destination_databend.client.DatabendClient", MagicMock())
def test_connection(config: Dict[str, str], logger: MagicMock) -> None:
    # Check no log object
    DatabendClient(**config)


@patch("destination_databend.writer.DatabendSQLWriter")
@patch("destination_databend.client.DatabendClient")
def test_sql_write_append(
        mock_connection: MagicMock,
        mock_writer: MagicMock,
        config: Dict[str, str],
        configured_stream1: ConfiguredAirbyteStream,
        configured_stream2: ConfiguredAirbyteStream,
        airbyte_message1: AirbyteMessage,
        airbyte_message2: AirbyteMessage,
        airbyte_state_message: AirbyteMessage,
) -> None:
    catalog = ConfiguredAirbyteCatalog(streams=[configured_stream1, configured_stream2])

    destination = DestinationDatabend()
    result = destination.write(config, catalog, [airbyte_message1, airbyte_state_message, airbyte_message2])

    assert list(result) == [airbyte_state_message]
    mock_writer.return_value.delete_table.assert_not_called()
    mock_writer.return_value.create_raw_table.mock_calls = [call(mock_connection, "table1"), call(mock_connection, "table2")]
    assert len(mock_writer.return_value.queue_write_data.mock_calls) == 2
    mock_writer.return_value.flush.assert_called_once()


@patch("destination_databend.writer.DatabendSQLWriter")
@patch("destination_databend.client.DatabendClient")
def test_sql_write_overwrite(
        mock_connection: MagicMock,
        mock_writer: MagicMock,
        config: Dict[str, str],
        configured_stream1: ConfiguredAirbyteStream,
        configured_stream2: ConfiguredAirbyteStream,
        airbyte_message1: AirbyteMessage,
        airbyte_message2: AirbyteMessage,
        airbyte_state_message: AirbyteMessage,
):
    # Overwrite triggers a delete
    configured_stream1.destination_sync_mode = DestinationSyncMode.overwrite
    catalog = ConfiguredAirbyteCatalog(streams=[configured_stream1, configured_stream2])

    destination = DestinationDatabend()
    result = destination.write(config, catalog, [airbyte_message1, airbyte_state_message, airbyte_message2])

    assert list(result) == [airbyte_state_message]
    mock_writer.return_value.delete_table.assert_called_once_with("table1")
    mock_writer.return_value.create_raw_table.mock_calls = [call(mock_connection, "table1"), call(mock_connection, "table2")]
