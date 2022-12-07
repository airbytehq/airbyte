#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
import logging
import time
from typing import Any, Dict, List, Mapping

import docker
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
from destination_weaviate import DestinationWeaviate
from destination_weaviate.client import Client


@pytest.fixture(name="config")
def config_fixture() -> Mapping[str, Any]:
    with open("integration_tests/example-config.json", "r") as f:
        return json.loads(f.read())


@pytest.fixture(name="configured_catalog")
def configured_catalog_fixture() -> ConfiguredAirbyteCatalog:
    stream_schema = {"type": "object", "properties": {"title": {"type": "str"}, "wordCount": {"type": "integer"}}}

    append_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(name="Article", json_schema=stream_schema, supported_sync_modes=[SyncMode.incremental]),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.append,
    )

    return ConfiguredAirbyteCatalog(streams=[append_stream])


@pytest.fixture(autouse=True)
def setup_teardown(config: Mapping):
    env_vars = {
        "QUERY_DEFAULTS_LIMIT": "25",
        "AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED": "true",
        "DEFAULT_VECTORIZER_MODULE": "none",
        "CLUSTER_HOSTNAME": "node1",
        "PERSISTENCE_DATA_PATH": "./data"
    }
    name = "weaviate-test-container-will-get-deleted"
    docker_client = docker.from_env()
    try:
        docker_client.containers.get(name).remove(force=True)
    except docker.errors.NotFound:
        pass

    docker_client.containers.run(
        "semitechnologies/weaviate:1.16.1", detach=True, environment=env_vars, name=name,
        ports={8080: ('127.0.0.1', 8081)}
    )

    retries = 3
    while retries > 0:
        try:
            Client(config)
            break
        except Exception as e:
            logging.info(f"error connecting to weaviate with client. Retrying in 1 second. Exception: {e}")
            time.sleep(1)
            retries -= 1

    yield
    docker_client.containers.get(name).remove(force=True)


@pytest.fixture(name="client")
def client_fixture(config) -> Client:
    return Client(config)


def test_check_valid_config(config: Mapping):
    outcome = DestinationWeaviate().check(AirbyteLogger(), config)
    assert outcome.status == Status.SUCCEEDED


def test_check_invalid_config():
    outcome = DestinationWeaviate().check(AirbyteLogger(), {"url": "localhost:6666"})
    assert outcome.status == Status.FAILED


def _state(data: Dict[str, Any]) -> AirbyteMessage:
    return AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(data=data))


def _record(stream: str, title: str, word_count: int) -> AirbyteMessage:
    return AirbyteMessage(
        type=Type.RECORD, record=AirbyteRecordMessage(stream=stream, data={"title": title, "wordCount": word_count}, emitted_at=0)
    )


def _record_with_id(stream: str, title: str, word_count: int, id: int) -> AirbyteMessage:
    return AirbyteMessage(
        type=Type.RECORD, record=AirbyteRecordMessage(stream=stream, data={
            "title": title,
            "wordCount": word_count,
            "id":  id
        }, emitted_at=0)
    )


def retrieve_all_records(client: Client) -> List[AirbyteRecordMessage]:
    """retrieves and formats all Articles as Airbyte messages"""
    all_records = client.client.data_object.get(class_name="Article")
    out = []
    for record in all_records.get("objects"):
        props = record["properties"]
        out.append(_record("Article", props["title"], props["wordCount"]))
    out.sort(key=lambda x: x.record.data.get("title"))
    return out


def test_write(config: Mapping, configured_catalog: ConfiguredAirbyteCatalog, client: Client):
    """
    This test verifies that:
        TODO: 1. writing a stream in "overwrite" mode overwrites any existing data for that stream
        2. writing a stream in "append" mode appends new records without deleting the old ones
        3. The correct state message is output by the connector at the end of the sync
    """
    append_stream = configured_catalog.streams[0].stream.name
    first_state_message = _state({"state": "1"})
    first_record_chunk = [_record(append_stream, str(i), i) for i in range(5)]

    destination = DestinationWeaviate()

    expected_states = [first_state_message]
    output_states = list(
        destination.write(
            config, configured_catalog, [*first_record_chunk, first_state_message]
        )
    )
    assert expected_states == output_states, "Checkpoint state messages were expected from the destination"

    expected_records = [_record(append_stream, str(i), i) for i in range(5)]
    records_in_destination = retrieve_all_records(client)
    assert expected_records == records_in_destination, "Records in destination should match records expected"

def test_write_id(config: Mapping, configured_catalog: ConfiguredAirbyteCatalog, client: Client):
    """
    This test verifies that records can have an ID that's an integer
    """
    append_stream = configured_catalog.streams[0].stream.name
    first_state_message = _state({"state": "1"})
    first_record_chunk = [_record_with_id(append_stream, str(i), i, i) for i in range(1, 6)]

    destination = DestinationWeaviate()

    expected_states = [first_state_message]
    output_states = list(
        destination.write(
            config, configured_catalog, [*first_record_chunk, first_state_message]
        )
    )
    assert expected_states == output_states, "Checkpoint state messages were expected from the destination"

    records_in_destination = retrieve_all_records(client)
    assert len(records_in_destination) == 5, "Expecting there should be 5 records"

    expected_records = [_record(append_stream, str(i), i) for i in range(1, 6)]
    for expected, actual in zip(expected_records, records_in_destination):
        assert expected.record.data.get("title") == actual.record.data.get("title"), "Titles should match"
        assert expected.record.data.get("wordCount") == actual.record.data.get("wordCount"), "Titles should match"
