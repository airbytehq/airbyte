#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import json
from typing import Any, Dict, List, Mapping

import pytest
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    Status,
    SyncMode,
    Type,
)
from destination_ngpvan import DestinationNgpvan
from destination_ngpvan.client import NGPVANClient


@pytest.fixture(name="config")
def config_fixture() -> Mapping[str, Any]:
    with open("secrets/config.json", "r") as f:
        return json.loads(f.read())


@pytest.fixture(name="configured_catalog")
def configured_catalog_fixture() -> ConfiguredAirbyteCatalog:
    stream_schema = {"type": "object", "properties": {"string_col": {"type": "str"}, "int_col": {"type": "integer"}}}

    append_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(name="append_stream", json_schema=stream_schema),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.append,
    )

    overwrite_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(name="overwrite_stream", json_schema=stream_schema),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.overwrite,
    )

    return ConfiguredAirbyteCatalog(streams=[append_stream, overwrite_stream])


@pytest.fixture(autouse=True)
def teardown(config: Mapping):
    yield
    client = NGPVANClient(**config)
    client.delete(list(client.list_keys()))

@pytest.fixture(name="client")
def client_fixture(config) -> NGPVANClient:
    return NGPVANClient(**config)

def test_check_valid_config(config: Mapping):
    outcome = DestinationNgpvan().check(AirbyteLogger(), config)
    assert outcome.status == Status.SUCCEEDED

def test_check_invalid_config():
    outcome = DestinationNgpvan().check(AirbyteLogger(), {"bucket_id": "not_a_real_id"})
    assert outcome.status == Status.FAILED

def _state(data: Dict[str, Any]) -> AirbyteMessage:
    return AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(data=data))

def _record(stream: str, str_value: str, int_value: int) -> AirbyteMessage:
    return AirbyteMessage(
        type=Type.RECORD, record=AirbyteRecordMessage(stream=stream, data={"str_col": str_value, "int_col": int_value}, emitted_at=0)
    )

def retrieve_all_records(client: NGPVANClient) -> List[AirbyteRecordMessage]:
    """retrieves and formats all records as Airbyte messages"""
    all_records = client.list_keys(list_values=True)
    out = []
    for record in all_records:
        key = record[0]
        stream = key.split("__ab__")[0]
        value = record[1]
        out.append(_record(stream, value["str_col"], value["int_col"]))
    return out

