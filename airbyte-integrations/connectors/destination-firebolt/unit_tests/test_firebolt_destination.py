#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from datetime import datetime
from typing import Any, Dict
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
from destination_firebolt.destination import DestinationFirebolt, establish_connection, parse_config
from pytest import fixture


@fixture(params=["my_engine", "my_engine.api.firebolt.io"])
def config(request: Any) -> Dict[str, str]:
    args = {
        "database": "my_database",
        "username": "my_username",
        "password": "my_password",
        "engine": request.param,
        "loading_method": {
            "method": "SQL",
        },
    }
    return args


@fixture
def config_external_table() -> Dict[str, str]:
    args = {
        "database": "my_database",
        "username": "my_username",
        "password": "my_password",
        "engine": "my_engine",
        "loading_method": {
            "method": "S3",
            "s3_bucket": "my_bucket",
            "s3_region": "us-east-1",
            "aws_key_id": "aws_key",
            "aws_key_secret": "aws_secret",
        },
    }
    return args


@fixture
def config_no_engine() -> Dict[str, str]:
    args = {
        "database": "my_database",
        "username": "my_username",
        "password": "my_password",
    }
    return args


@fixture
def logger() -> MagicMock:
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


def test_parse_config(config: Dict[str, str]):
    config["engine"] = "override_engine"
    result = parse_config(config)
    assert result["database"] == "my_database"
    assert result["engine_name"] == "override_engine"
    assert result["auth"].username == "my_username"
    assert result["auth"].password == "my_password"
    config["engine"] = "override_engine.api.firebolt.io"
    result = parse_config(config)
    assert result["engine_url"] == "override_engine.api.firebolt.io"


@patch("destination_firebolt.destination.connect", MagicMock())
def test_connection(config: Dict[str, str], config_no_engine: Dict[str, str], logger: MagicMock) -> None:
    establish_connection(config, logger)
    logger.reset_mock()
    establish_connection(config_no_engine, logger)
    assert any(["default engine" in msg.args[0] for msg in logger.info.mock_calls]), "No message on using default engine"
    # Check no log object
    establish_connection(config)


@patch("destination_firebolt.writer.FireboltS3Writer")
@patch("destination_firebolt.destination.connect")
def test_check(
    mock_connection: MagicMock, mock_writer: MagicMock, config: Dict[str, str], config_external_table: Dict[str, str], logger: MagicMock
):
    destination = DestinationFirebolt()
    status = destination.check(logger, config)
    assert status.status == Status.SUCCEEDED
    mock_writer.assert_not_called()
    status = destination.check(logger, config_external_table)
    assert status.status == Status.SUCCEEDED
    mock_writer.assert_called_once()
    mock_connection().__enter__().cursor().__enter__().execute.side_effect = Exception("my exception")
    status = destination.check(logger, config)
    assert status.status == Status.FAILED


@patch("destination_firebolt.writer.FireboltSQLWriter")
@patch("destination_firebolt.destination.establish_connection")
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

    destination = DestinationFirebolt()
    result = destination.write(config, catalog, [airbyte_message1, airbyte_state_message, airbyte_message2])

    assert list(result) == [airbyte_state_message]
    mock_writer.return_value.delete_table.assert_not_called()
    mock_writer.return_value.create_raw_table.mock_calls = [call(mock_connection, "table1"), call(mock_connection, "table2")]
    assert len(mock_writer.return_value.queue_write_data.mock_calls) == 2
    mock_writer.return_value.flush.assert_called_once()


@patch("destination_firebolt.writer.FireboltS3Writer")
@patch("destination_firebolt.writer.FireboltSQLWriter")
@patch("destination_firebolt.destination.establish_connection")
def test_sql_write_overwrite(
    mock_connection: MagicMock,
    mock_writer: MagicMock,
    mock_s3_writer: MagicMock,
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

    destination = DestinationFirebolt()
    result = destination.write(config, catalog, [airbyte_message1, airbyte_state_message, airbyte_message2])

    mock_s3_writer.assert_not_called()
    assert list(result) == [airbyte_state_message]
    mock_writer.return_value.delete_table.assert_called_once_with("table1")
    mock_writer.return_value.create_raw_table.mock_calls = [call(mock_connection, "table1"), call(mock_connection, "table2")]


@patch("destination_firebolt.writer.FireboltS3Writer")
@patch("destination_firebolt.writer.FireboltSQLWriter")
@patch("destination_firebolt.destination.establish_connection", MagicMock())
def test_s3_write(
    mock_sql_writer: MagicMock,
    mock_s3_writer: MagicMock,
    config_external_table: Dict[str, str],
    configured_stream1: ConfiguredAirbyteStream,
    configured_stream2: ConfiguredAirbyteStream,
    airbyte_message1: AirbyteMessage,
    airbyte_message2: AirbyteMessage,
    airbyte_state_message: AirbyteMessage,
):
    catalog = ConfiguredAirbyteCatalog(streams=[configured_stream1, configured_stream2])

    destination = DestinationFirebolt()
    result = destination.write(config_external_table, catalog, [airbyte_message1, airbyte_state_message, airbyte_message2])
    assert list(result) == [airbyte_state_message]
    mock_sql_writer.assert_not_called()
    mock_s3_writer.assert_called_once()
