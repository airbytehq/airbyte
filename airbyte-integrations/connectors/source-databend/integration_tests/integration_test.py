#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import random
import string
from json import load
from typing import Dict, Generator
from unittest.mock import MagicMock

from airbyte_cdk.models import Status, AirbyteConnectionStatus
from airbyte_cdk.models.airbyte_protocol import (
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    SyncMode,
)
from databend_sqlalchemy.connector import Cursor
from pytest import fixture
from source_databend.source import SourceDatabend, establish_conn


@fixture(scope="module")
def test_table_name() -> str:
    letters = string.ascii_lowercase
    rnd_string = "".join(random.choice(letters) for i in range(10))
    return f"airbyte_integration_{rnd_string}"


@fixture(scope="module")
def test_view_name(test_table_name) -> str:
    return f"view_{test_table_name}"


@fixture(scope="module", autouse=True)
def create_test_databend_data(config: Dict[str, str], test_table_name: str, test_view_name: str):
    print("creating table and view....", test_table_name, test_view_name)
    try:
        cursor = establish_conn(**config)
        cursor.execute(
            f"CREATE TABLE IF NOT EXISTS {test_table_name}(column1 STRING NULL, column2 INT NULL, column3 DATE NULL, column4 DATETIME NULL, column5 INT NULL, column6 ARRAY(UINT8), column7 BOOLEAN NULL)"
        )
        cursor.execute(
            f"INSERT INTO TABLE {test_table_name} VALUES ('my_value',221,'2021-01-01','2021-01-01 12:00:01', Null, [1,2,3], true), ('my_value2',null,'2021-01-02','2021-01-02 12:00:02',11, [1,2,3], null)"
        )
        cursor.execute(f"CREATE VIEW  IF NOT EXISTS {test_view_name} AS SELECT column1, column2 FROM {test_table_name}")
    except Exception as e:
        return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(e)}")


@fixture
def table_schema() -> str:
    schema = {
        "type": "object",
        "properties": {
            "column1": {"type": ["null", "string"]},
            "column2": {"type": ["null", "integer"]},
            "column3": {"type": ["null", "string"], "format": "date"},
            "column4": {
                "type": ["null", "string"],
                "format": "datetime",
                "airbyte_type": "timestamp_without_timezone",
            },
            "column5": {"type": ["null", "integer"]},
            "column6": {"type": "array", "items": {"type": ["null", "string"]}},
            "column7": {"type": ["null", "integer"]},
        },
    }
    return schema


@fixture
def test_stream(test_table_name: str, table_schema: str) -> AirbyteStream:
    return AirbyteStream(name=test_table_name, json_schema=table_schema, supported_sync_modes=[SyncMode.full_refresh])


@fixture
def view_schema() -> str:
    schema = {
        "type": "object",
        "properties": {
            "column1": {"type": ["null", "string"]},
            "column2": {"type": ["null", "integer"]},
        },
    }
    return schema


@fixture
def test_view_stream(test_view_name: str, view_schema: str) -> AirbyteStream:
    return AirbyteStream(name=test_view_name, json_schema=view_schema, supported_sync_modes=[SyncMode.full_refresh])


@fixture
def configured_catalogue(test_table_name: str, table_schema: str) -> ConfiguredAirbyteCatalog:
    # Deleting one column to simulate manipulation in UI
    del table_schema["properties"]["column1"]
    append_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(name=test_table_name, json_schema=table_schema, supported_sync_modes=[SyncMode.full_refresh]),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.append,
    )
    return ConfiguredAirbyteCatalog(streams=[append_stream])


@fixture
def configured_view_catalogue(test_view_name: str, view_schema: str) -> ConfiguredAirbyteCatalog:
    append_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(name=test_view_name, json_schema=view_schema, supported_sync_modes=[SyncMode.full_refresh]),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.append,
    )
    return ConfiguredAirbyteCatalog(streams=[append_stream])


@fixture(scope="module")
def config() -> Dict[str, str]:
    with open(
            "secrets/config.json",
    ) as f:
        yield load(f)


@fixture(scope="module")
def invalid_config() -> Dict[str, str]:
    with open(
            "integration_tests/invalid_config.json",
    ) as f:
        yield load(f)


@fixture(scope="module", autouse=True)
def teardown(config: Dict[str, str], test_table_name: str, test_view_name: str):
    yield
    cursor = establish_conn(**config)
    cursor.execute(f"DROP TABLE {test_table_name}")
    cursor.execute(f"DROP VIEW {test_view_name}")
    cursor.close()


def test_check_fails(invalid_config: Dict[str, str]):
    source = SourceDatabend()
    status = source.check(logger=MagicMock(), config=invalid_config)
    assert status.status == Status.FAILED


def test_check_succeeds(config: Dict[str, str]):
    source = SourceDatabend()
    status = source.check(logger=MagicMock(), config=config)
    assert status.status == Status.SUCCEEDED


def test_discover(
        config: Dict[str, str],
        test_table_name: str,
        test_view_name: str,
        test_stream: AirbyteStream,
        test_view_stream: AirbyteStream,
):
    source = SourceDatabend()
    catalog = source.discover(MagicMock(), config)
    assert any(stream.name == test_table_name for stream in catalog.streams), "Test table not found"
    for stream in catalog.streams:
        if stream.name == test_table_name:
            assert stream == test_stream


def test_read(
        config: Dict[str, str],
        test_table_name: str,
        configured_catalogue: ConfiguredAirbyteCatalog,
):
    expected_data = [
        {"column2": 221, "column3": "2021-01-01", "column4": "2021-01-01 12:00:01.000000", "column5": "NULL", "column6": [1, 2, 3],
         "column7": True},
        {
            "column2": "NULL",
            "column3": "2021-01-02",
            "column4": "2021-01-02 12:00:02.000000",
            "column5": 11,
            "column6": [1, 2, 3],
            "column7": "NULL"
        },
    ]
    source = SourceDatabend()
    result = source.read(logger=MagicMock(), config=config, catalog=configured_catalogue, state={})
    data = list(result)
    assert all([x.record.stream == test_table_name for x in data]), "Table name is incorrect"
    assert [x.record.data for x in data] == expected_data, "Test data is not matching"


def test_view_read(
        config: Dict[str, str],
        test_view_name: str,
        configured_view_catalogue: ConfiguredAirbyteCatalog,
):
    expected_data = [
        {"column1": "my_value", "column2": 221},
        {
            "column1": "my_value2",
            "column2": "NULL"
        },
    ]
    source = SourceDatabend()
    result = source.read(logger=MagicMock(), config=config, catalog=configured_view_catalogue, state={})
    data = list(result)
    assert all([x.record.stream == test_view_name for x in data]), "Table name is incorrect"
    assert [x.record.data for x in data] == expected_data, "Test data is not matching"
