#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
from typing import Any, Dict, Mapping

import pytest
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
from destination_meilisearch.destination import DestinationMeilisearch, get_client
from meilisearch import Client


@pytest.fixture(name="config")
def config_fixture() -> Mapping[str, Any]:
    with open("secrets/config.json", "r") as f:
        return json.loads(f.read())


@pytest.fixture(name="configured_catalog")
def configured_catalog_fixture() -> ConfiguredAirbyteCatalog:
    stream_schema = {"type": "object", "properties": {"string_col": {"type": "str"}, "int_col": {"type": "integer"}}}

    overwrite_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(
            name="_airbyte", json_schema=stream_schema, supported_sync_modes=[SyncMode.incremental, SyncMode.full_refresh]
        ),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.overwrite,
    )

    return ConfiguredAirbyteCatalog(streams=[overwrite_stream])


@pytest.fixture(autouse=True)
def teardown(config: Mapping):
    yield
    client = get_client(config=config)
    client.delete_index("_airbyte")


@pytest.fixture(name="client")
def client_fixture(config) -> Client:
    client = get_client(config=config)
    resp = client.create_index("_airbyte", {"primaryKey": "_ab_pk"})
    client.wait_for_task(_handle_breaking_wait_for_task(resp))
    return client


def test_check_valid_config(config: Mapping):
    outcome = DestinationMeilisearch().check(logging.getLogger("airbyte"), config)
    assert outcome.status == Status.SUCCEEDED


def test_check_invalid_config():
    outcome = DestinationMeilisearch().check(
        logging.getLogger("airbyte"), {"api_key": "not_a_real_key", "host": "https://www.meilisearch.com"}
    )
    assert outcome.status == Status.FAILED


def _state(data: Dict[str, Any]) -> AirbyteMessage:
    return AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(data=data))


def _record(stream: str, str_value: str, int_value: int) -> AirbyteMessage:
    return AirbyteMessage(
        type=Type.RECORD, record=AirbyteRecordMessage(stream=stream, data={"str_col": str_value, "int_col": int_value}, emitted_at=0)
    )


def _handle_breaking_wait_for_task(task: Any) -> int:
    if type(task) is dict:
        return task["taskUid"]
    else:
        return task.task_uid


def records_count(client: Client) -> int:
    documents_results = client.index("_airbyte").get_documents()
    return documents_results.total


def test_write(config: Mapping, configured_catalog: ConfiguredAirbyteCatalog, client: Client):
    overwrite_stream = configured_catalog.streams[0].stream.name
    first_state_message = _state({"state": "1"})
    first_record_chunk = [_record(overwrite_stream, str(i), i) for i in range(2)]

    destination = DestinationMeilisearch()
    list(destination.write(config, configured_catalog, [*first_record_chunk, first_state_message]))
    assert records_count(client) == 2
