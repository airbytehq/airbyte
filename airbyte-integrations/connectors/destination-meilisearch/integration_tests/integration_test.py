#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
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
from meilisearch import Client

from destination_meilisearch.destination import DestinationMeilisearch, get_client

INDEX = "movies"


@pytest.fixture(name="config")
def config_fixture() -> Mapping[str, Any]:
    with open("secrets/config.json", "r") as f:
        return json.loads(f.read())


@pytest.fixture(name="client")
def client_fixture(config: Mapping[str, Any]) -> Client:
    return get_client(config)


@pytest.fixture(autouse=True)
def teardown(client: Client):
    yield
    try:
        client.delete_index(INDEX)
    except Exception:
        pass


def _catalog(sync_mode: DestinationSyncMode) -> ConfiguredAirbyteCatalog:
    stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(
            name=INDEX,
            json_schema={"type": "object", "properties": {"id": {"type": "integer"}, "title": {"type": "string"}}},
            supported_sync_modes=[SyncMode.incremental, SyncMode.full_refresh],
        ),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=sync_mode,
        primary_key=[["id"]],
    )
    return ConfiguredAirbyteCatalog(streams=[stream])


def _record(data: Dict[str, Any]) -> AirbyteMessage:
    return AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream=INDEX, data=data, emitted_at=0))


def _state() -> AirbyteMessage:
    return AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(data={}))


def test_check_valid_config(config: Mapping[str, Any]):
    outcome = DestinationMeilisearch().check(logging.getLogger("airbyte"), config)
    assert outcome.status == Status.SUCCEEDED


def test_check_invalid_config():
    outcome = DestinationMeilisearch().check(
        logging.getLogger("airbyte"), {"host": "http://localhost:1", "api_key": "nope"}
    )
    assert outcome.status == Status.FAILED


def test_append_dedup_uses_natural_key_and_upserts(config: Mapping[str, Any], client: Client):
    destination = DestinationMeilisearch()
    list(destination.write(config, _catalog(DestinationSyncMode.append_dedup), [_record({"id": 1, "title": "first"}), _state()]))
    list(destination.write(config, _catalog(DestinationSyncMode.append_dedup), [_record({"id": 1, "title": "second"}), _state()]))
    doc = client.index(INDEX).get_document(1)
    assert doc.title == "second"  # same natural key -> upsert, not a duplicate


def test_merge_preserves_untouched_fields(config: Mapping[str, Any], client: Client):
    destination = DestinationMeilisearch()
    list(destination.write(config, _catalog(DestinationSyncMode.append_dedup), [_record({"id": 2, "title": "keep", "year": 1999}), _state()]))

    merge_config = {**config, "update_method": "merge"}
    list(destination.write(merge_config, _catalog(DestinationSyncMode.append_dedup), [_record({"id": 2, "title": "updated"}), _state()]))
    doc = client.index(INDEX).get_document(2)
    assert doc.title == "updated"
    assert doc.year == 1999  # field absent from the merge record survives


def test_overwrite_replaces_index(config: Mapping[str, Any], client: Client):
    destination = DestinationMeilisearch()
    list(destination.write(config, _catalog(DestinationSyncMode.overwrite), [_record({"id": 10, "title": "old"}), _state()]))
    list(destination.write(config, _catalog(DestinationSyncMode.overwrite), [_record({"id": 20, "title": "new"}), _state()]))
    docs = client.index(INDEX).get_documents()
    ids = {d.id for d in docs.results}
    assert ids == {20}  # overwrite wiped the previous sync


def test_overwrite_with_zero_records_keeps_empty_index(config: Mapping[str, Any], client: Client):
    destination = DestinationMeilisearch()
    list(destination.write(config, _catalog(DestinationSyncMode.overwrite), [_record({"id": 1, "title": "x"}), _state()]))
    list(destination.write(config, _catalog(DestinationSyncMode.overwrite), [_state()]))
    index = client.get_index(INDEX)  # index must survive an empty sync
    assert index.primary_key == "id"
    assert client.index(INDEX).get_documents().total == 0


def test_append_dedup_fails_fast_on_primary_key_mismatch(config: Mapping[str, Any], client: Client):
    # Simulate an index created by connector v1 (primaryKey _ab_pk).
    task = client.index(INDEX).add_documents([{"_ab_pk": "abc", "title": "old"}], "_ab_pk")
    client.wait_for_task(task.task_uid, 60_000, 200)

    destination = DestinationMeilisearch()
    with pytest.raises(ValueError, match="already has primary key '_ab_pk'"):
        list(destination.write(config, _catalog(DestinationSyncMode.append_dedup), [_record({"id": 1, "title": "new"}), _state()]))
