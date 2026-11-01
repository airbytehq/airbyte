#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
import logging
import os
import uuid
from pathlib import Path
from typing import Any, Dict, List, Mapping

import pytest
from destination_meilisearch import DestinationMeilisearch
from destination_meilisearch.client import TaskFailedError
from destination_meilisearch.writer import PRIMARY_KEY
from meilisearch import Client

from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateMessage,
    AirbyteStateType,
    AirbyteStream,
    AirbyteStreamStatus,
    AirbyteStreamStatusTraceMessage,
    AirbyteTraceMessage,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    Status,
    StreamDescriptor,
    SyncMode,
    TraceType,
    Type,
)


@pytest.fixture(name="config")
def config_fixture() -> Mapping[str, Any]:
    secrets = Path(__file__).parent.parent / "secrets" / "config.json"
    if secrets.exists():
        return json.loads(secrets.read_text())
    # A local instance, such as the one in docker-compose.yaml.
    return {
        "host": os.environ.get("MEILISEARCH_HOST", "http://localhost:7700"),
        "api_key": os.environ.get("MEILISEARCH_API_KEY", "masterKey"),
    }


@pytest.fixture(name="stream_name")
def stream_name_fixture(config) -> str:
    name = f"airbyte_test_{uuid.uuid4().hex[:8]}"
    yield name
    client = Client(config["host"], config.get("api_key"))
    client.wait_for_task(client.delete_index(name).task_uid)


def catalog(name: str, mode: DestinationSyncMode, **kwargs) -> ConfiguredAirbyteCatalog:
    return ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(name=name, json_schema={"type": "object"}, supported_sync_modes=[SyncMode.incremental]),
                sync_mode=SyncMode.incremental,
                destination_sync_mode=mode,
                **kwargs,
            )
        ]
    )


def record(stream: str, data: Dict[str, Any]) -> AirbyteMessage:
    return AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream=stream, data=data, emitted_at=0))


def state(value: int) -> AirbyteMessage:
    return AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(type=AirbyteStateType.LEGACY, data={"cursor": value}))


def complete(stream: str) -> AirbyteMessage:
    return AirbyteMessage(
        type=Type.TRACE,
        trace=AirbyteTraceMessage(
            type=TraceType.STREAM_STATUS,
            emitted_at=0,
            stream_status=AirbyteStreamStatusTraceMessage(
                stream_descriptor=StreamDescriptor(name=stream), status=AirbyteStreamStatus.COMPLETE
            ),
        ),
    )


def documents(config: Mapping[str, Any], index: str) -> List[Dict[str, Any]]:
    client = Client(config["host"], config.get("api_key"))
    docs = client.index(index).get_documents({"limit": 1000}).results
    return sorted((dict(d) for d in docs), key=lambda d: d[PRIMARY_KEY])


def strip(docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [{k: v for k, v in d.items() if not k.startswith("_")} for d in docs]


def test_check(config):
    destination = DestinationMeilisearch()
    assert destination.check(logging.getLogger("airbyte"), config).status == Status.SUCCEEDED

    bad = {**config, "api_key": "not-a-valid-key"}
    status = destination.check(logging.getLogger("airbyte"), bad)
    assert status.status == Status.FAILED
    assert "invalid_api_key" in status.message


def test_append_dedup_with_cdc_deletes(config, stream_name):
    destination = DestinationMeilisearch()
    messages = [
        record(stream_name, {"id": 1, "name": "one"}),
        record(stream_name, {"id": 2, "name": "two"}),
        record(stream_name, {"id": "a@b", "name": "hashed key"}),
        state(1),
        record(stream_name, {"id": 1, "name": "one, updated"}),
        record(stream_name, {"id": 2, "name": "two", "_ab_cdc_deleted_at": "2026-01-01T00:00:00Z"}),
        record(stream_name, {"id": 3, "name": "three", "nested": {"tags": ["x", "y"]}}),
        state(2),
    ]
    output = list(destination.write(config, catalog(stream_name, DestinationSyncMode.append_dedup, primary_key=[["id"]]), iter(messages)))
    assert [m.state.data for m in output] == [{"cursor": 1}, {"cursor": 2}]

    docs = documents(config, stream_name)
    assert [d[PRIMARY_KEY] for d in docs if not d[PRIMARY_KEY].startswith("h_")] == ["1", "3"]
    assert strip(docs) == [
        {"id": 1, "name": "one, updated"},
        {"id": 3, "name": "three", "nested": {"tags": ["x", "y"]}},
        {"id": "a@b", "name": "hashed key"},
    ]

    # Syncing the same records again doesn't duplicate them.
    list(destination.write(config, catalog(stream_name, DestinationSyncMode.append_dedup, primary_key=[["id"]]), iter(messages)))
    assert len(documents(config, stream_name)) == 3


def test_append(config, stream_name):
    destination = DestinationMeilisearch()
    messages = [record(stream_name, {"id": 1}), record(stream_name, {"id": 1}), state(1)]
    list(destination.write({**config, "batch_size": 1}, catalog(stream_name, DestinationSyncMode.append), iter(messages)))
    list(destination.write(config, catalog(stream_name, DestinationSyncMode.append), iter(messages)))
    assert strip(documents(config, stream_name)) == [{"id": 1}] * 4


def test_overwrite_without_generations(config, stream_name):
    destination = DestinationMeilisearch()
    list(destination.write(config, catalog(stream_name, DestinationSyncMode.append), iter([record(stream_name, {"id": 1}), state(1)])))
    list(destination.write(config, catalog(stream_name, DestinationSyncMode.overwrite), iter([record(stream_name, {"id": 2}), state(1)])))
    assert strip(documents(config, stream_name)) == [{"id": 2}]


def test_refresh_deletes_earlier_generations_once_complete(config, stream_name):
    destination = DestinationMeilisearch()

    def sync(generation: int, minimum: int, messages: List[AirbyteMessage]):
        cat = catalog(
            stream_name,
            DestinationSyncMode.append_dedup,
            primary_key=[["id"]],
            generation_id=generation,
            minimum_generation_id=minimum,
        )
        list(destination.write(config, cat, iter(messages)))

    sync(1, 0, [record(stream_name, {"id": 1}), record(stream_name, {"id": 2}), state(1), complete(stream_name)])
    assert [d["_airbyte_generation_id"] for d in documents(config, stream_name)] == [1, 1]

    # A refresh which doesn't complete keeps the documents of the earlier generation.
    sync(2, 2, [record(stream_name, {"id": 2}), state(1)])
    docs = documents(config, stream_name)
    assert [(d["id"], d["_airbyte_generation_id"]) for d in docs] == [(1, 1), (2, 2)]

    # Once it completes, they are deleted.
    sync(2, 2, [record(stream_name, {"id": 3}), state(2), complete(stream_name)])
    docs = documents(config, stream_name)
    assert [(d["id"], d["_airbyte_generation_id"]) for d in docs] == [(2, 2), (3, 2)]

    # Settings configured on the index are kept.
    settings = Client(config["host"], config.get("api_key")).index(stream_name).get_settings()
    assert "_airbyte_generation_id" in settings["filterableAttributes"]


def test_invalid_document_fails_without_emitting_state(config, stream_name):
    destination = DestinationMeilisearch()
    list(destination.write(config, catalog(stream_name, DestinationSyncMode.append_dedup, primary_key=[["id"]]), iter([])))
    # Meilisearch rejects documents with a malformed _geo attribute once it is
    # filterable.
    client = Client(config["host"], config.get("api_key"))
    client.wait_for_task(client.index(stream_name).update_filterable_attributes(["_geo"]).task_uid)

    messages = [
        record(stream_name, {"id": 1}),
        state(1),
        record(stream_name, {"id": 2, "_geo": "not a location"}),
        state(2),
    ]
    output = []
    # A batch size of 1 checkpoints at every state message.
    with pytest.raises(TaskFailedError, match="invalid_document_geo_field"):
        for message in destination.write(
            {**config, "batch_size": 1}, catalog(stream_name, DestinationSyncMode.append_dedup, primary_key=[["id"]]), iter(messages)
        ):
            output.append(message)
    assert [m.state.data for m in output] == [{"cursor": 1}]
