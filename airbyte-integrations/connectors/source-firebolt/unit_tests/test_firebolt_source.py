#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from datetime import date, datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch

from pytest import fixture, mark
from source_firebolt.database import get_table_structure, parse_config
from source_firebolt.source import SUPPORTED_SYNC_MODES, SourceFirebolt, convert_type, establish_connection
from source_firebolt.utils import airbyte_message_from_data, format_fetch_result

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


@fixture(params=["my_engine", "my_engine.api.firebolt.io"])
def config(request):
    args = {
        "database": "my_database",
        "client_id": "my_id",
        "client_secret": "my_secret",
        "engine": request.param,
    }
    return args


@fixture()
def legacy_config(request):
    args = {
        "database": "my_database",
        # @ is important here to determine the auth type
        "username": "my@username",
        "password": "my_password",
        "engine": "my_engine",
    }
    return args


@fixture()
def config_no_engine():
    args = {
        "database": "my_database",
        "client_id": "my_id",
        "client_secret": "my_secret",
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
    return [("col1", "STRING", 0), ("col2", "INT", 0)]


@fixture
def table2_structure():
    return [("col3", "ARRAY", 0), ("col4", "DECIMAL", 0)]


@fixture
def logger():
    return MagicMock()


def test_parse_config(config, logger):
    config["engine"] = "override_engine"
    result = parse_config(config, logger)
    assert result["database"] == "my_database"
    assert result["engine_name"] == "override_engine"
    assert result["auth"].client_id == "my_id"
    assert result["auth"].client_secret == "my_secret"
    config["engine"] = "override_engine.api.firebolt.io"
    result = parse_config(config, logger)
    assert result["engine_url"] == "override_engine.api.firebolt.io"


def test_parse_legacy_config(legacy_config, logger):
    result = parse_config(legacy_config, logger)
    assert result["database"] == "my_database"
    assert result["auth"].username == "my@username"
    assert result["auth"].password == "my_password"


@patch("source_firebolt.database.connect")
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
        ("DECIMAL(4,15)", False, {"type": "string", "airbyte_type": "big_number"}),
        (
            "TIMESTAMP",
            False,
            {
                "type": "string",
                "format": "date-time",
                "airbyte_type": "timestamp_without_timezone",
            },
        ),
        ("ARRAY(ARRAY(INT NOT NULL))", False, {"type": "array", "items": {"type": "array", "items": {"type": ["null", "integer"]}}}),
        ("int", True, {"type": ["null", "integer"]}),
        ("DUMMY", False, {"type": "string"}),
        ("boolean", False, {"type": "boolean"}),
        ("pgdate", False, {"type": "string", "format": "date"}),
        (
            "TIMESTAMPNTZ",
            False,
            {
                "type": "string",
                "format": "datetime",
                "airbyte_type": "timestamp_without_timezone",
            },
        ),
        (
            "TIMESTAMPTZ",
            False,
            {
                "type": "string",
                "format": "datetime",
                "airbyte_type": "timestamp_with_timezone",
            },
        ),
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
        ([[date.fromisoformat("0019-01-01"), 2], 0.2214], [["0019-01-01", 2], 0.2214]),
        ([[date.fromisoformat("2019-01-01"), 2], 0.2214], [["2019-01-01", 2], 0.2214]),
        ([[None, 2], None], [[None, 2], None]),
        ([Decimal("1231232.123459999990457054844258706536")], ["1231232.123459999990457054844258706536"]),
        ([datetime.fromisoformat("2019-01-01 20:12:02+01:30"), 2], ["2019-01-01T20:12:02+01:30", 2]),
        ([True, 2], [True, 2]),
    ],
)
def test_format_fetch_result(data, expected):
    assert format_fetch_result(data) == expected


@patch("source_firebolt.utils.datetime")
def test_airbyte_message_from_data(mock_datetime):
    mock_datetime.now.return_value.timestamp.return_value = 10
    raw_data = [1, "a", [1, 2, 3]]
    columns = ["Col1", "Col2", "Col3"]
    table_name = "dummy"
    expected = AirbyteMessage(
        type=Type.RECORD,
        record=AirbyteRecordMessage(
            stream="dummy",
            data={"Col1": 1, "Col2": "a", "Col3": [1, 2, 3]},
            emitted_at=10000,
        ),
    )
    result = airbyte_message_from_data(raw_data, columns, table_name)
    assert result == expected


def test_airbyte_message_from_data_no_data():
    raw_data = []
    columns = ["Col1", "Col2"]
    table_name = "dummy"
    result = airbyte_message_from_data(raw_data, columns, table_name)
    assert result is None


@patch("source_firebolt.source.establish_connection")
def test_check(mock_connection, config, logger):
    source = SourceFirebolt()
    status = source.check(logger, config)
    assert status.status == Status.SUCCEEDED
    mock_connection().__enter__().cursor().__enter__().execute.side_effect = Exception("my exception")
    status = source.check(logger, config)
    assert status.status == Status.FAILED


@patch("source_firebolt.source.get_table_structure")
@patch("source_firebolt.source.establish_connection")
def test_discover(
    mock_establish_connection,
    mock_get_structure,
    config,
    stream1,
    stream2,
    table1_structure,
    table2_structure,
    logger,
):
    mock_get_structure.return_value = {"table1": table1_structure, "table2": table2_structure}

    source = SourceFirebolt()
    catalog = source.discover(logger, config)
    assert catalog.streams[0].name == "table1"
    assert catalog.streams[1].name == "table2"
    assert catalog.streams[0].json_schema == stream1.json_schema
    assert catalog.streams[1].json_schema == stream2.json_schema


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


def test_get_table_structure(table1_structure, table2_structure):
    # Query results contain table names as well
    table1_query_result = [("table1",) + (item) for item in table1_structure]
    table2_query_result = [("table2",) + (item) for item in table2_structure]
    connection = MagicMock()
    connection.cursor().fetchall.return_value = table1_query_result + table2_query_result
    result = get_table_structure(connection)
    assert result["table1"] == table1_structure
    assert result["table2"] == table2_structure
