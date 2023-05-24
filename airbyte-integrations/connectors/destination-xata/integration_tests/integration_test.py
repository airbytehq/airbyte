#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json

from unittest.mock import Mock
from typing import Any, Dict, List, Mapping

from destination_xata import DestinationXata

import pytest
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
    return ConfiguredAirbyteCatalog(streams=[append_stream,]) # overwrite_stream])

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

    records = [AirbyteMessage(
        type=Type.RECORD, record=AirbyteRecordMessage(stream="test_stream", data={
            "str_col": "example",
            "int_col": 1,
        }, emitted_at=0)
    )]
    dest = DestinationXata()
    dest.write(
        config=config, 
        configured_catalog=test_stream,
        input_messages=records
    )
