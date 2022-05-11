#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from datetime import datetime
from unittest.mock import MagicMock, call, patch

from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    Status,
    SyncMode,
    Type,
)
from destination_firebolt.destination import DestinationFirebolt, establish_connection
from pytest import fixture


@fixture(params=["my_engine", "my_engine.api.firebolt.io"])
def config(request):
    args = {
        "database": "my_database",
        "username": "my_username",
        "password": "my_password",
        "engine": request.param,
    }
    return args


@fixture
def config_external_table():
    args = {
        "database": "my_database",
        "username": "my_username",
        "password": "my_password",
        "engine": "my_engine",
        "s3_bucket": "my_bucket",
        "s3_region": "us-east-1",
        "aws_key_id": "aws_key",
        "aws_key_secret": "aws_secret",
    }
    return args


@fixture
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
            name="table1",
            json_schema={
                "type": "object",
                "properties": {"col1": {"type": "string"}, "col2": {"type": "integer"}},
            },
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
        ),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.append,
    )


@fixture
def airbyte_message1():
    return AirbyteMessage(
        type=Type.RECORD,
        record=AirbyteRecordMessage(
            stream="table1",
            data={"key1": "value1", "key2": 2},
            emitted_at=int(datetime.now().timestamp()) * 1000,
        ),
    )


@fixture
def airbyte_message2():
    return AirbyteMessage(
        type=Type.RECORD,
        record=AirbyteRecordMessage(
            stream="table2",
            data={"key1": "value2", "key2": 3},
            emitted_at=int(datetime.now().timestamp()) * 1000,
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
def test_check(mock_connection, config, config_external_table, logger):
    destination = DestinationFirebolt()
    status = destination.check(logger, config)
    assert status.status == Status.SUCCEEDED
    status = destination.check(logger, config_external_table)
    assert status.status == Status.SUCCEEDED
    mock_connection().__enter__().cursor().__enter__().execute.side_effect = Exception("my exception")
    status = destination.check(logger, config)
    assert status.status == Status.FAILED


@patch("destination_firebolt.destination.FireboltSQLWriter")
@patch("destination_firebolt.destination.establish_connection")
def test_sql_write_append(
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


@patch("destination_firebolt.destination.FireboltS3Writer")
@patch("destination_firebolt.destination.FireboltSQLWriter")
@patch("destination_firebolt.destination.establish_connection")
def test_sql_write_overwrite(
    mock_connection,
    mock_writer,
    mock_s3_writer,
    config,
    configured_stream1,
    configured_stream2,
    airbyte_message1,
    airbyte_message2,
    airbyte_state_message,
):
    # Overwrite triggers a delete
    configured_stream1.destination_sync_mode = DestinationSyncMode.overwrite
    catalog = ConfiguredAirbyteCatalog(streams=[configured_stream1, configured_stream2])

    destination = DestinationFirebolt()
    result = destination.write(config, catalog, [airbyte_message1, airbyte_state_message, airbyte_message2])

    mock_s3_writer.assert_not_called()
    assert list(result) == [airbyte_state_message]
    mock_writer.return_value.delete_table.assert_called_once_with("table1")
    mock_writer.return_value.create_raw_table.mock_calls = [call(mock_connection, "table1"), call(mock_connection, "table2")]


@patch("destination_firebolt.destination.FireboltS3Writer")
@patch("destination_firebolt.destination.FireboltSQLWriter")
@patch("destination_firebolt.destination.establish_connection", MagicMock())
def test_s3_write(
    mock_sql_writer,
    mock_s3_writer,
    config_external_table,
    configured_stream1,
    configured_stream2,
    airbyte_message1,
    airbyte_message2,
    airbyte_state_message,
):
    catalog = ConfiguredAirbyteCatalog(streams=[configured_stream1, configured_stream2])

    destination = DestinationFirebolt()
    result = destination.write(config_external_table, catalog, [airbyte_message1, airbyte_state_message, airbyte_message2])
    assert list(result) == [airbyte_state_message]
    mock_sql_writer.assert_not_called()
    mock_s3_writer.assert_called_once()
