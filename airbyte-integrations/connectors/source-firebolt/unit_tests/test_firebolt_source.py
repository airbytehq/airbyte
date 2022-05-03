#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from datetime import date, datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

from airbyte_cdk.models import AirbyteStream, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, DestinationSyncMode, Status, SyncMode
from pytest import fixture, mark
from source_firebolt.source import (
    SUPPORTED_SYNC_MODES,
    SourceFirebolt,
    convert_type,
    establish_connection,
    get_firebolt_tables,
    get_table_stream,
)
from source_firebolt.utils import format_fetch_result


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
def stream1() -> AirbyteStream:
    stream1 = AirbyteStream(
        name="table1",
        supported_sync_modes=SUPPORTED_SYNC_MODES,
        json_schema={
            "type": "object",
            "properties": {"col1": {"type": "string"}, "col2": {"type": "integer"}},
        },
    )
    return stream1


@fixture
def stream2() -> AirbyteStream:
    stream2 = AirbyteStream(
        name="table2",
        supported_sync_modes=SUPPORTED_SYNC_MODES,
        json_schema={
            "type": "object",
            "properties": {
                "col3": {"type": "array", "items": {"type": ["null", "string"]}},
                "col4": {"type": "string", "airbyte_type": "big_number"},
            },
        },
    )
    return stream2


@fixture
def table1_structure():
    return [("table1", "col1", "STRING", 0), ("table1", "col2", "INT", 0)]


@fixture
def table2_structure():
    return [("table2", "col3", "ARRAY", 0), ("table2", "col4", "DECIMAL", 0)]


@fixture
def logger():
    return MagicMock()


@fixture(name="mock_connection")
def async_connection_cursor_mock():
    connection = MagicMock()
    cursor = AsyncMock()
    connection.cursor.return_value = cursor
    return connection, cursor


@patch("source_firebolt.source.connect")
def test_connection(mock_connection, config, config_no_engine, logger):
    establish_connection(config, logger)
    logger.reset_mock()
    establish_connection(config_no_engine, logger)
    assert any(["default engine" in msg.args[0] for msg in logger.info.mock_calls]), "No message on using default engine"


@mark.parametrize(
    "type,nullable,result",
    [
        ("VARCHAR", False, {"type": "string"}),
        ("INT", False, {"type": "integer"}),
        ("int", False, {"type": "integer"}),
        ("LONG", False, {"type": "integer"}),
        (
            "TIMESTAMP",
            False,
            {
                "type": "string",
                "format": "datetime",
                "airbyte_type": "timestamp_without_timezone",
            },
        ),
        ("ARRAY(ARRAY(INT))", False, {"type": "array", "items": {"type": "array", "items": {"type": ["null", "integer"]}}}),
        ("int", True, {"type": ["null", "integer"]}),
        ("DUMMY", False, {"type": "string"}),
    ],
)
def test_convert_type(type, nullable, result):
    assert convert_type(type, nullable) == result


@mark.parametrize(
    "data,expected",
    [
        (
            ["a", 1],
            ["a", 1],
        ),
        ([datetime.fromisoformat("2019-01-01 20:12:02"), 2], ["2019-01-01T20:12:02", 2]),
        ([[date.fromisoformat("2019-01-01"), 2], 0.2214], [["2019-01-01", 2], 0.2214]),
        ([[None, 2], None], [[None, 2], None]),
        ([Decimal("1231232.123459999990457054844258706536")], ["1231232.123459999990457054844258706536"]),
    ],
)
def test_format_fetch_result(data, expected):
    assert format_fetch_result(data) == expected


@mark.asyncio
async def test_get_firebolt_tables(mock_connection):
    connection, cursor = mock_connection
    cursor.fetchall.return_value = [("table1",), ("table2",)]
    result = await get_firebolt_tables(connection)
    assert result == ["table1", "table2"]


@mark.asyncio
async def test_get_table_stream(mock_connection, table1_structure, stream1):
    connection, cursor = mock_connection
    cursor.fetchall.return_value = table1_structure
    result = await get_table_stream(connection, "table1")
    assert result == stream1


@patch("source_firebolt.source.establish_connection")
def test_check(mock_connection, config, logger):
    source = SourceFirebolt()
    status = source.check(logger, config)
    assert status.status == Status.SUCCEEDED
    mock_connection().__enter__().cursor().__enter__().execute.side_effect = Exception("my exception")
    status = source.check(logger, config)
    assert status.status == Status.FAILED


@patch("source_firebolt.source.get_table_stream")
@patch("source_firebolt.source.establish_async_connection")
def test_discover(
    mock_establish_connection,
    mock_get_stream,
    mock_connection,
    config,
    stream1,
    stream2,
    logger,
):
    connection, cursor = mock_connection
    cursor.fetchall.return_value = ["table1", "table2"]
    mock_establish_connection.return_value.__aenter__.return_value = connection
    mock_get_stream.side_effect = [stream1, stream2]

    source = SourceFirebolt()
    catalog = source.discover(logger, config)
    assert catalog.streams[0].name == "table1"
    assert catalog.streams[1].name == "table2"
    assert catalog.streams[0].json_schema == stream1.json_schema
    assert catalog.streams[1].json_schema == stream2.json_schema
    mock_establish_connection.assert_awaited_once_with(config, logger)


@patch("source_firebolt.source.establish_connection")
def test_read_no_state(mock_connection, config, stream1, logger):
    source = SourceFirebolt()

    c_stream = ConfiguredAirbyteStream(
        sync_mode=SyncMode.full_refresh,
        destination_sync_mode=DestinationSyncMode.overwrite,
        stream=stream1,
    )
    catalog = ConfiguredAirbyteCatalog(streams=[c_stream])
    mock_connection().__enter__().cursor().__enter__().fetchall().__iter__.return_value = iter(
        [
            ["s_value1", 1],
            ["s_value2", 2],
        ]
    )
    message1 = next(source.read(logger, config, catalog, {}))
    assert message1.record.stream == stream1.name
    assert message1.record.data == {"col1": "s_value1", "col2": 1}
    message2 = next(source.read(logger, config, catalog, {}))
    assert message2.record.stream == stream1.name
    assert message2.record.data == {"col1": "s_value2", "col2": 2}


@patch("source_firebolt.source.establish_connection")
def test_read_special_types_no_state(mock_connection, config, stream2, logger):
    source = SourceFirebolt()

    c_stream = ConfiguredAirbyteStream(
        sync_mode=SyncMode.full_refresh,
        destination_sync_mode=DestinationSyncMode.overwrite,
        stream=stream2,
    )
    catalog = ConfiguredAirbyteCatalog(streams=[c_stream])
    mock_connection().__enter__().cursor().__enter__().fetchall().__iter__.return_value = iter(
        [
            [
                [datetime.fromisoformat("2019-01-01 20:12:02"), datetime.fromisoformat("2019-02-01 20:12:02")],
                Decimal("1231232.123459999990457054844258706536"),
            ],
        ]
    )

    message1 = next(source.read(logger, config, catalog, {}))
    assert message1.record.stream == stream2.name
    assert message1.record.data == {
        "col3": ["2019-01-01T20:12:02", "2019-02-01T20:12:02"],
        "col4": "1231232.123459999990457054844258706536",
    }
