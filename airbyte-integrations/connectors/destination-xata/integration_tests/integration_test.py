#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from typing import Any, Mapping
from unittest.mock import Mock

import pytest
from destination_xata import DestinationXata
from xata.client import XataClient

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


@pytest.fixture(name="config")
def config_fixture() -> Mapping[str, Any]:
    with open("secrets/config.json", "r") as f:
        return json.loads(f.read())


@pytest.fixture(name="configured_catalog")
def configured_catalog_fixture() -> ConfiguredAirbyteCatalog:
    stream_schema = {"type": "object", "properties": {"string_col": {"type": "str"}, "int_col": {"type": "integer"}}}

    append_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(name="append_stream", json_schema=stream_schema, supported_sync_modes=[SyncMode.incremental]),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.append,
    )
    # TODO implement overwrite
    """
    overwrite_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(name="overwrite_stream", json_schema=stream_schema, supported_sync_modes=[SyncMode.incremental]),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.overwrite,
    )
    """
    return ConfiguredAirbyteCatalog(streams=[append_stream])


def test_check_valid_config(config: Mapping):
    outcome = DestinationXata().check(logger=Mock(), config=config)
    assert outcome.status == Status.SUCCEEDED


def test_check_invalid_config():
    f = open("integration_tests/invalid_config.json")
    config = json.load(f)
    outcome = DestinationXata().check(logger=Mock(), config=config)
    assert outcome.status == Status.FAILED


def test_write(config: Mapping):
    test_schema = {"type": "object", "properties": {"str_col": {"type": "str"}, "int_col": {"type": "integer"}}}

    test_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(name="test_stream", json_schema=test_schema, supported_sync_modes=[SyncMode.incremental]),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.append,
    )

    records = [
        AirbyteMessage(
            type=Type.RECORD,
            record=AirbyteRecordMessage(
                stream="test_stream",
                data={
                    "str_col": "example",
                    "int_col": 1,
                },
                emitted_at=0,
            ),
        )
    ]

    # setup Xata workspace
    xata = XataClient(api_key=config["api_key"], db_url=config["db_url"])
    db_name = xata.get_config()["dbName"]
    # database exists ?
    assert xata.databases().getDatabaseMetadata(db_name).status_code == 200, f"database '{db_name}' does not exist."
    assert xata.table().createTable("test_stream").status_code == 201, "could not create table, if it already exists, please delete it."
    assert (
        xata.table()
        .setTableSchema(
            "test_stream",
            {
                "columns": [
                    {"name": "str_col", "type": "string"},
                    {"name": "int_col", "type": "int"},
                ]
            },
        )
        .status_code
        == 200
    ), "failed to set table schema"

    dest = DestinationXata()
    list(dest.write(config=config, configured_catalog=test_stream, input_messages=records))

    # fetch record
    records = xata.data().queryTable("test_stream", {})
    assert records.status_code == 200
    assert len(records.json()["records"]) == 1

    proof = records.json()["records"][0]
    assert proof["str_col"] == "example"
    assert proof["int_col"] == 1

    # cleanup
    assert xata.table().deleteTable("test_stream").status_code == 200
