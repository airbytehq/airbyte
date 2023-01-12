#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from datetime import date, datetime
from decimal import Decimal
from typing import Dict
from unittest.mock import AsyncMock, MagicMock, call, patch
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
from pytest import fixture, mark
from source_databend.source import SUPPORTED_SYNC_MODES, SourceDatabend, convert_type, establish_conn, get_table_structure
from source_databend.utils import airbyte_message_from_data, format_fetch_result


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
                "col4": {"type": "integer"},
            },
        },
    )
    return stream2


@fixture
def table1_structure():
    return [("col1", "STRING", 0), ("col2", "INT", 0)]


@fixture
def table2_structure():
    return [("col3", "ARRAY", 0), ("col4", "BIGINT", 0)]


@fixture
def logger() -> MagicMock:
    return MagicMock()


@fixture(name="mock_open")
def async_connection_cursor_mock(config: Dict[str, str]):
    establish_conn = MagicMock()
    cursor = MagicMock()
    establish_conn.return_value = cursor

    return establish_conn, cursor


@patch("source_databend.client.connector", MagicMock())
def test_connection(config: Dict[str, str], logger: MagicMock) -> None:
    # Check no log object
    cursor = establish_conn(**config)
    cursor.execute("select 1")


@patch("source_databend.client.connector", MagicMock())
def test_check(mock_open, config, logger):
    source = SourceDatabend()
    status = source.check(logger, config)
    assert status.status == Status.SUCCEEDED


@mark.parametrize(
    "type,nullable,result",
    [
        ("VARCHAR", False, {"type": "string"}),
        ("INT", False, {"type": "integer"}),
        ("int", False, {"type": "integer"}),
        ("DOUBLE", False, {"type": "number"}),
        (
                "TIMESTAMP",
                False,
                {
                    "type": "string",
                    "format": "datetime",
                    "airbyte_type": "timestamp_without_timezone",
                },
        ),
        ("int", True, {"type": ["null", "integer"]}),
        ("boolean", False, {"type": "integer"}),
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
    ],
)
def test_format_fetch_result(data, expected):
    assert format_fetch_result(data) == expected


@patch("source_databend.utils.datetime")
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


@patch("source_databend.source.get_table_structure")
def test_discover(
        mock_get_structure,
        config,
        stream1,
        stream2,
        table1_structure,
        table2_structure,
        logger,
):
    mock_get_structure.return_value = {"table1": table1_structure, "table2": table2_structure}

    source = SourceDatabend()
    catalog = source.discover(logger, config)
    assert catalog.streams[0].name == "table1"
    assert catalog.streams[1].name == "table2"
    assert catalog.streams[0].json_schema == stream1.json_schema
    assert catalog.streams[1].json_schema == stream2.json_schema


@patch("source_databend.source.establish_conn")
def test_read_no_state(mock_open, config, stream1, logger):
    mock_cursor = mock_open.return_value
    source = SourceDatabend()

    c_stream = ConfiguredAirbyteStream(
        sync_mode=SyncMode.full_refresh,
        destination_sync_mode=DestinationSyncMode.overwrite,
        stream=stream1,
    )
    catalog = ConfiguredAirbyteCatalog(streams=[c_stream])
    mock_cursor.fetchall.return_value = iter(
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


@patch("source_databend.source.establish_conn")
def test_read_special_types_no_state(mock_open, config, stream2, logger):
    mock_cursor = mock_open.return_value
    source = SourceDatabend()

    c_stream = ConfiguredAirbyteStream(
        sync_mode=SyncMode.full_refresh,
        destination_sync_mode=DestinationSyncMode.overwrite,
        stream=stream2,
    )
    catalog = ConfiguredAirbyteCatalog(streams=[c_stream])
    mock_cursor.fetchall.return_value = iter(
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


@patch("source_databend.source.establish_conn")
def test_get_table_structure(mock_open, config, table1_structure, table2_structure):
    mock_cursor = mock_open.return_value
    table1_query_result = [("table1",) + (item) for item in table1_structure]
    table2_query_result = [("table2",) + (item) for item in table2_structure]
    mock_cursor.fetchall.return_value = table1_query_result + table2_query_result
    result = get_table_structure(mock_cursor)
    assert result["table1"] == table1_structure
    assert result["table2"] == table2_structure
