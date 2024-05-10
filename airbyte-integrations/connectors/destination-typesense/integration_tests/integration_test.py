#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from typing import Any, Dict, Mapping

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
from destination_typesense.destination import DestinationTypesense, get_client
from typesense import Client


@pytest.fixture(name="config")
def config_fixture() -> Mapping[str, Any]:
    with open("secrets/config.json", "r") as f:
        return json.loads(f.read())


@pytest.fixture(name="configured_catalog")
def configured_catalog_fixture() -> ConfiguredAirbyteCatalog:
    stream_schema = {"type": "object", "properties": {"col1": {"type": "str"}, "col2": {"type": "integer"}}}

    overwrite_stream = lambda n: ConfiguredAirbyteStream(
        stream=AirbyteStream(name=f"_airbyte_{n}", json_schema=stream_schema, supported_sync_modes=[SyncMode.incremental]),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.overwrite,
    )

    return ConfiguredAirbyteCatalog(streams=[overwrite_stream(i) for i in range(2)])


@pytest.fixture(autouse=True)
def teardown(config: Mapping):
    yield
    client = get_client(config=config)
    try:
        client.collections["_airbyte"].delete()
    except Exception:
        pass


@pytest.fixture(name="client")
def client_fixture(config) -> Client:
    client = get_client(config=config)
    client.collections.create({"name": "_airbyte", "fields": [{"name": ".*", "type": "auto"}]})
    return client


def test_check_valid_config(config: Mapping):
    outcome = DestinationTypesense().check(AirbyteLogger(), config)
    assert outcome.status == Status.SUCCEEDED


def test_check_invalid_config():
    outcome = DestinationTypesense().check(AirbyteLogger(), {"api_key": "not_a_real_key", "host": "https://www.fake.com"})
    assert outcome.status == Status.FAILED


def _state(data: Dict[str, Any]) -> AirbyteMessage:
    return AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(data=data))


def _record(stream: str, str_value: str, int_value: int) -> AirbyteMessage:
    return AirbyteMessage(
        type=Type.RECORD, record=AirbyteRecordMessage(stream=stream, data={"str_col": str_value, "int_col": int_value}, emitted_at=0)
    )


def collection_size(client: Client, stream: str) -> int:
    collection = client.collections[stream].retrieve()
    return collection["num_documents"]


def test_write(config: Mapping, configured_catalog: ConfiguredAirbyteCatalog, client: Client):
    configured_streams = list(map(lambda s: s.stream.name, configured_catalog.streams))
    first_state_message = _state({"state": "1"})
    first_record_chunk = [_record(stream, str(i), i) for i, stream in enumerate(configured_streams)]

    destination = DestinationTypesense()
    list(destination.write(config, configured_catalog, [*first_record_chunk, first_state_message]))

    for stream in configured_streams:
        assert collection_size(client, stream) == 1
