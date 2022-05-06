#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock, call, patch
from pytest import fixture
from destination_firebolt.destination import DestinationFirebolt, FireboltWriter, establish_connection
from airbyte_cdk.models import (
    Status,
    ConfiguredAirbyteStream,
    AirbyteStream,
    SyncMode,
    DestinationSyncMode,
    ConfiguredAirbyteCatalog,
    AirbyteMessage,
    Type,
    AirbyteRecordMessage,
)
from datetime import datetime


@fixture(params=["my_engine", "my_engine.api.firebolt.io"])
def config(request):
    args = {
        "database": "my_database",
        "username": "my_username",
        "password": "my_password",
        "engine": request.param,
    }
    return args


@fixture()
def config_no_engine():
    args = {
        "database": "my_database",
        "username": "my_username",
        "password": "my_password",
    }
    return args


@fixture
def logger():
    return MagicMock()


@fixture
def configured_stream1() -> ConfiguredAirbyteStream:
    return ConfiguredAirbyteStream(
        stream=AirbyteStream(
            name="table1", json_schema={"type": "object", "properties": {"col1": {"type": "string"}, "col2": {"type": "integer"}},}
        ),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.append,
    )


@fixture
def configured_stream2() -> ConfiguredAirbyteStream:
    return ConfiguredAirbyteStream(
        stream=AirbyteStream(
            name="table2", json_schema={"type": "object", "properties": {"col1": {"type": "string"}, "col2": {"type": "integer"}},}
        ),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.append,
    )


@fixture
def airbyte_message1():
    return AirbyteMessage(
        type=Type.RECORD,
        record=AirbyteRecordMessage(
            stream="table1", data={"key1": "value1", "key2": 2}, emitted_at=int(datetime.now().timestamp()) * 1000,
        ),
    )


@fixture
def airbyte_message2():
    return AirbyteMessage(
        type=Type.RECORD,
        record=AirbyteRecordMessage(
            stream="table2", data={"key1": "value2", "key2": 3}, emitted_at=int(datetime.now().timestamp()) * 1000,
        ),
    )


@fixture
def airbyte_state_message():
    return AirbyteMessage(type=Type.STATE)


@patch("destination_firebolt.destination.connect")
def test_connection(mock_connection, config, config_no_engine, logger):
    establish_connection(config, logger)
    logger.reset_mock()
    establish_connection(config_no_engine, logger)
    assert any(["default engine" in msg.args[0] for msg in logger.info.mock_calls]), "No message on using default engine"
    # Check no log object
    establish_connection(config)


@patch("destination_firebolt.destination.connect")
def test_check(mock_connection, config, logger):
    destination = DestinationFirebolt()
    status = destination.check(logger, config)
    assert status.status == Status.SUCCEEDED
    mock_connection().__enter__().cursor().__enter__().execute.side_effect = Exception("my exception")
    status = destination.check(logger, config)
    assert status.status == Status.FAILED


@patch("destination_firebolt.destination.FireboltWriter")
@patch("destination_firebolt.destination.establish_connection")
def test_write_append(
    mock_connection, mock_writer, config, configured_stream1, configured_stream2, airbyte_message1, airbyte_message2, airbyte_state_message
):
    catalog = ConfiguredAirbyteCatalog(streams=[configured_stream1, configured_stream2])

    destination = DestinationFirebolt()
    result = destination.write(config, catalog, [airbyte_message1, airbyte_state_message, airbyte_message2])

    assert list(result) == [airbyte_state_message]
    mock_writer.return_value.delete_table.assert_not_called()
    mock_writer.return_value.create_raw_table.mock_calls = [call(mock_connection, "table1"), call(mock_connection, "table2")]
    assert len(mock_writer.return_value.queue_write_data.mock_calls) == 2
    mock_writer.return_value.flush.assert_called_once()


@patch("destination_firebolt.destination.FireboltWriter")
@patch("destination_firebolt.destination.establish_connection")
def test_write_overwrite(
    mock_connection, mock_writer, config, configured_stream1, configured_stream2, airbyte_message1, airbyte_message2, airbyte_state_message
):
    # Overwrite triggers a delete
    configured_stream1.destination_sync_mode = DestinationSyncMode.overwrite
    catalog = ConfiguredAirbyteCatalog(streams=[configured_stream1, configured_stream2])

    destination = DestinationFirebolt()
    result = destination.write(config, catalog, [airbyte_message1, airbyte_state_message, airbyte_message2])

    assert list(result) == [airbyte_state_message]
    mock_writer.return_value.delete_table.assert_called_once_with("table1")
    mock_writer.return_value.create_raw_table.mock_calls = [call(mock_connection, "table1"), call(mock_connection, "table2")]


def test_writer_delete():
    connection = MagicMock()
    writer = FireboltWriter(connection)

    writer.delete_table("my_new_table")
    connection.cursor.return_value.execute.assert_called_once_with("DROP TABLE IF EXISTS _airbyte_raw_my_new_table")


def test_writer_no_flush():
    connection = MagicMock()
    writer = FireboltWriter(connection)

    sample_data = [
        ("t1", "id1", 111, '{"a": 1}'),
        ("t1", "id2", 112, '{"b": 1}'),
        ("t2", "id1", 113, '{"c": 1}'),
        ("t1", "id1", 114, '{"d": 1}'),
    ]
    for table, id, time, data in sample_data:
        writer.queue_write_data(table, id, time, data)
    assert list(writer.buffer.keys()) == ["t1", "t2"]
    assert writer.buffer["t1"] == [("id1", 111, '{"a": 1}'), ("id2", 112, '{"b": 1}'), ("id1", 114, '{"d": 1}')]
    assert writer.buffer["t2"] == [("id1", 113, '{"c": 1}')]
    # No write until we flush
    connection.cursor.return_value.executemany.assert_not_called()

    query1 = "INSERT INTO _airbyte_raw_t1 VALUES (?, ?, ?)"
    query2 = "INSERT INTO _airbyte_raw_t2 VALUES (?, ?, ?)"
    writer.flush()
    assert connection.cursor.return_value.executemany.mock_calls == [
        call(query1, parameters_seq=[("id1", 111, '{"a": 1}'), ("id2", 112, '{"b": 1}'), ("id1", 114, '{"d": 1}')]),
        call(query2, parameters_seq=[("id1", 113, '{"c": 1}')]),
    ]


def test_writer_flush():
    connection = MagicMock()
    writer = FireboltWriter(connection)

    writer.flush_interval = 3

    sample_data = [
        ("t1", "id1", 111, '{"a": 1}'),
        ("t1", "id2", 112, '{"b": 1}'),
        ("t2", "id1", 113, '{"c": 1}'),
        ("t1", "id1", 114, '{"d": 1}'),
    ]
    for table, id, time, data in sample_data:
        writer.queue_write_data(table, id, time, data)
    assert list(writer.buffer.keys()) == ["t1"]
    assert writer.buffer["t1"] == [("id1", 114, '{"d": 1}')]
    assert "t2" not in writer.buffer.keys()

    query1 = "INSERT INTO _airbyte_raw_t1 VALUES (?, ?, ?)"
    query2 = "INSERT INTO _airbyte_raw_t2 VALUES (?, ?, ?)"
    assert connection.cursor.return_value.executemany.mock_calls == [
        call(query1, parameters_seq=[("id1", 111, '{"a": 1}'), ("id2", 112, '{"b": 1}')]),
        call(query2, parameters_seq=[("id1", 113, '{"c": 1}')]),
    ]

    connection.cursor.return_value.executemany.reset_mock()
    writer.flush()
    assert connection.cursor.return_value.executemany.mock_calls == [call(query1, parameters_seq=[("id1", 114, '{"d": 1}')])]
