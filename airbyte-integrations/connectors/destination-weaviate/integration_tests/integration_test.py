#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
import logging
import time
from typing import Any, Dict, List, Mapping
import os

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


def create_catalog(stream_name: str, stream_schema: Mapping[str, Any]) -> ConfiguredAirbyteCatalog:
    append_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(name=stream_name, json_schema=stream_schema, supported_sync_modes=[SyncMode.incremental]),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.append,
    )
    return ConfiguredAirbyteCatalog(streams=[append_stream])


@pytest.fixture(name="article_catalog")
def article_catalog_fixture() -> ConfiguredAirbyteCatalog:
    stream_schema = {"type": "object", "properties": {"title": {"type": "str"}, "wordCount": {"type": "integer"}}}

    append_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(name="Article", json_schema=stream_schema, supported_sync_modes=[SyncMode.incremental]),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.append,
    )

    return ConfiguredAirbyteCatalog(streams=[append_stream])


def load_json_file(path: str) -> Mapping:
    dirname = os.path.dirname(__file__)
    file = open(os.path.join(dirname, path))
    return json.load(file)


@pytest.fixture(name="pokemon_catalog")
def pokemon_catalog_fixture() -> ConfiguredAirbyteCatalog:
    stream_schema = load_json_file("pokemon-schema.json")

    append_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(name="pokemon", json_schema=stream_schema, supported_sync_modes=[SyncMode.incremental]),
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
    time.sleep(0.5)

    retries = 3
    while retries > 0:
        try:
            Client(config, {})
            break
        except Exception as e:
            logging.info(f"error connecting to weaviate with client. Retrying in 1 second. Exception: {e}")
            time.sleep(1)
            retries -= 1

    yield
    docker_client.containers.get(name).remove(force=True)


@pytest.fixture(name="client")
def client_fixture(config) -> Client:
    return Client(config, {})


def test_check_valid_config(config: Mapping):
    outcome = DestinationWeaviate().check(AirbyteLogger(), config)
    assert outcome.status == Status.SUCCEEDED


def test_check_invalid_config():
    outcome = DestinationWeaviate().check(AirbyteLogger(), {"url": "localhost:6666"})
    assert outcome.status == Status.FAILED


def _state(data: Dict[str, Any]) -> AirbyteMessage:
    return AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(data=data))


def _record(stream: str, data: Mapping[str, Any]) -> AirbyteMessage:
    return AirbyteMessage(
        type=Type.RECORD, record=AirbyteRecordMessage(stream=stream, data=data, emitted_at=0)
    )


def _article_record(stream: str, title: str, word_count: int) -> AirbyteMessage:
    return AirbyteMessage(
        type=Type.RECORD, record=AirbyteRecordMessage(stream=stream, data={"title": title, "wordCount": word_count}, emitted_at=0)
    )


def _pikachu_record():
    data = load_json_file("pokemon-pikachu.json")
    return AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream="pokemon", data=data, emitted_at=0))


def _record_with_id(stream: str, title: str, word_count: int, id: int) -> AirbyteMessage:
    return AirbyteMessage(
        type=Type.RECORD, record=AirbyteRecordMessage(stream=stream, data={
            "title": title,
            "wordCount": word_count,
            "id":  id
        }, emitted_at=0)
    )


def retrieve_all_articles(client: Client) -> List[AirbyteRecordMessage]:
    """retrieves and formats all Articles as Airbyte messages"""
    all_records = client.client.data_object.get(class_name="Article", )
    out = []
    for record in all_records.get("objects"):
        props = record["properties"]
        out.append(_article_record("Article", props["title"], props["wordCount"]))
    out.sort(key=lambda x: x.record.data.get("title"))
    return out


def get_objects(client: Client, class_name: str) -> List[Mapping[str, Any]]:
    """retrieves and formats all Articles as Airbyte messages"""
    all_records = client.client.data_object.get(class_name=class_name, with_vector=True)
    return all_records.get("objects")


def count_objects(client: Client, class_name: str) -> int:
    result = client.client.query.aggregate(class_name) \
        .with_fields('meta { count }') \
        .do()
    return result["data"]["Aggregate"][class_name][0]["meta"]["count"]


def test_write(config: Mapping, article_catalog: ConfiguredAirbyteCatalog, client: Client):
    """
    This test verifies that:
        TODO: 1. writing a stream in "overwrite" mode overwrites any existing data for that stream
        2. writing a stream in "append" mode appends new records without deleting the old ones
        3. The correct state message is output by the connector at the end of the sync
    """
    append_stream = article_catalog.streams[0].stream.name
    first_state_message = _state({"state": "1"})
    first_record_chunk = [_article_record(append_stream, str(i), i) for i in range(5)]

    destination = DestinationWeaviate()

    expected_states = [first_state_message]
    output_states = list(
        destination.write(
            config, article_catalog, [*first_record_chunk, first_state_message]
        )
    )
    assert expected_states == output_states, "Checkpoint state messages were expected from the destination"

    expected_records = [_article_record(append_stream, str(i), i) for i in range(5)]
    records_in_destination = retrieve_all_articles(client)
    assert expected_records == records_in_destination, "Records in destination should match records expected"


def test_write_large_batch(config: Mapping, article_catalog: ConfiguredAirbyteCatalog, client: Client):
    append_stream = article_catalog.streams[0].stream.name
    first_state_message = _state({"state": "1"})
    first_record_chunk = [_article_record(append_stream, str(i), i) for i in range(400)]

    destination = DestinationWeaviate()

    expected_states = [first_state_message]
    output_states = list(
        destination.write(
            config, article_catalog, [*first_record_chunk, first_state_message]
        )
    )
    assert expected_states == output_states, "Checkpoint state messages were expected from the destination"
    assert count_objects(client, "Article") == 400, "There should be 400 records in weaviate"


def test_write_second_sync(config: Mapping, article_catalog: ConfiguredAirbyteCatalog, client: Client):
    append_stream = article_catalog.streams[0].stream.name
    first_state_message = _state({"state": "1"})
    second_state_message = _state({"state": "2"})
    first_record_chunk = [_article_record(append_stream, str(i), i) for i in range(5)]

    destination = DestinationWeaviate()

    expected_states = [first_state_message, second_state_message]
    output_states = list(
        destination.write(
            config, article_catalog, [*first_record_chunk, first_state_message, *first_record_chunk, second_state_message]
        )
    )
    assert expected_states == output_states, "Checkpoint state messages were expected from the destination"
    assert count_objects(client, "Article") == 10, "First and second state should have flushed a total of 10 articles"


def test_line_break_characters(config: Mapping, client: Client):
    stream_name = "currency"
    stream_schema = load_json_file("exchange_rate_catalog.json")
    catalog = create_catalog(stream_name, stream_schema)
    first_state_message = _state({"state": "1"})
    data = {"id": 1, "currency": "USD\u2028", "date": "2020-03-\n31T00:00:00Z\r", "HKD": 10.1, "NZD": 700.1}
    first_record_chunk = [_record(stream_name, data)]

    destination = DestinationWeaviate()

    expected_states = [first_state_message]
    output_states = list(
        destination.write(
            config, catalog, [*first_record_chunk, first_state_message]
        )
    )
    assert expected_states == output_states, "Checkpoint state messages were expected from the destination"
    assert count_objects(client, "Currency") == 1, "There should be only 1 object of class currency in Weaviate"
    actual = get_objects(client, "Currency")[0]
    assert actual["properties"].get("date") == data.get("date"), "Dates with new line should match"
    assert actual["properties"].get("hKD") == data.get("HKD"), "HKD should match hKD in Weaviate"
    assert actual["properties"].get("nZD") == data.get("NZD")
    assert actual["properties"].get("currency") == data.get("currency")


def test_write_id(config: Mapping, article_catalog: ConfiguredAirbyteCatalog, client: Client):
    """
    This test verifies that records can have an ID that's an integer
    """
    append_stream = article_catalog.streams[0].stream.name
    first_state_message = _state({"state": "1"})
    first_record_chunk = [_record_with_id(append_stream, str(i), i, i) for i in range(1, 6)]

    destination = DestinationWeaviate()

    expected_states = [first_state_message]
    output_states = list(
        destination.write(
            config, article_catalog, [*first_record_chunk, first_state_message]
        )
    )
    assert expected_states == output_states, "Checkpoint state messages were expected from the destination"

    records_in_destination = retrieve_all_articles(client)
    assert len(records_in_destination) == 5, "Expecting there should be 5 records"

    expected_records = [_article_record(append_stream, str(i), i) for i in range(1, 6)]
    for expected, actual in zip(expected_records, records_in_destination):
        assert expected.record.data.get("title") == actual.record.data.get("title"), "Titles should match"
        assert expected.record.data.get("wordCount") == actual.record.data.get("wordCount"), "Titles should match"


def test_write_pokemon_source_pikachu(config: Mapping, pokemon_catalog: ConfiguredAirbyteCatalog, client: Client):
    destination = DestinationWeaviate()

    first_state_message = _state({"state": "1"})
    pikachu = _pikachu_record()
    output_states = list(
        destination.write(
            config, pokemon_catalog, [pikachu, first_state_message]
        )
    )

    expected_states = [first_state_message]
    assert expected_states == output_states, "Checkpoint state messages were expected from the destination"

    records_in_destination = get_objects(client, "Pokemon")
    assert len(records_in_destination) == 1, "Expecting there should be 1 record"

    actual = records_in_destination[0]
    assert actual["properties"]["name"] == pikachu.record.data.get("name"), "Names should match"


def test_upload_vector(config: Mapping, client: Client):
    stream_name = "article_with_vector"
    stream_schema = {"type": "object", "properties": {
        "title": {"type": "string"},
        "vector": {"type": "array", "items": {"type": "number}"}}
    }}
    catalog = create_catalog(stream_name, stream_schema)
    first_state_message = _state({"state": "1"})
    data = {"title": "test1", "vector": [0.1, 0.2]}
    first_record_chunk = [_record(stream_name, data)]

    destination = DestinationWeaviate()
    config["vectors"] = "article_with_vector.vector"

    expected_states = [first_state_message]
    output_states = list(
        destination.write(
            config, catalog, [*first_record_chunk, first_state_message]
        )
    )
    assert expected_states == output_states, "Checkpoint state messages were expected from the destination"

    class_name = "Article_With_Vector"
    assert count_objects(client, class_name) == 1, "There should be only 1 object of in Weaviate"
    actual = get_objects(client, class_name)[0]
    assert actual.get("vector") == data.get("vector"), "Vectors should match"
