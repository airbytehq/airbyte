#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
from types import SimpleNamespace
from typing import Any, List
from unittest.mock import MagicMock

import pytest
from meilisearch.errors import MeilisearchApiError, MeilisearchCommunicationError

from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateMessage,
    AirbyteStateType,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    SyncMode,
    Type,
)
from destination_meilisearch.client import MAX_ATTEMPTS, MeiliClient, TaskFailedError, with_retry
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from destination_meilisearch.destination import DestinationMeilisearch, check_unique_indexes, stream_index, truncation_generation
from destination_meilisearch.writer import PRIMARY_KEY, StreamWriter, document_id, extract_key, index_uid


def api_error(status: int, code: str = "internal") -> MeilisearchApiError:
    response = SimpleNamespace(status_code=status, text=json.dumps({"message": "boom", "code": code}))
    return MeilisearchApiError("boom", response)


def test_index_uid():
    assert index_uid("users") == "users"
    assert index_uid("users", "public") == "public_users"
    assert index_uid("my stream.v2/x") == "my_stream_v2_x"
    assert len(index_uid("a" * 500)) == 400


def test_document_id():
    assert document_id([42]) == "42"
    assert document_id(["user-1_a"]) == "user-1_a"
    # Values which aren't valid document IDs, and composite keys, are hashed.
    hashed = document_id(["user@example.com"])
    assert hashed.startswith("h_") and len(hashed) == 66
    assert document_id([1, "a"]) == document_id([1, "a"])
    assert document_id([1, "a"]) != document_id(["a", 1])
    assert document_id([True]).startswith("h_")
    assert document_id(["x" * 600]).startswith("h_")


def test_extract_key():
    data = {"id": 1, "nested": {"key": "a"}}
    assert extract_key(data, [["id"], ["nested", "key"]]) == [1, "a"]
    with pytest.raises(ValueError, match="nested.missing"):
        extract_key(data, [["nested", "missing"]])


class FakeClient:
    """Records the requests a StreamWriter makes."""

    def __init__(self):
        self.requests: List[Any] = []
        self.client = MagicMock()
        self.client.index.return_value.add_documents_ndjson.side_effect = lambda payload, primary_key: self._add(payload)
        self.client.index.return_value.delete_documents.side_effect = lambda ids: self._delete(ids)

    def _add(self, payload: bytes):
        docs = [json.loads(line) for line in payload.decode().splitlines()]
        self.requests.append(("add", docs))
        return SimpleNamespace(task_uid=len(self.requests))

    def _delete(self, ids):
        self.requests.append(("delete", list(ids)))
        return SimpleNamespace(task_uid=len(self.requests))

    def enqueue(self, description, fn):
        return fn().task_uid


def test_writer_dedup_keeps_operations_in_order():
    client = FakeClient()
    writer = StreamWriter(client, "idx", batch_size=100, primary_key=[["id"]], generation_id=3)

    writer.write({"id": 1, "v": "a"})
    writer.write({"id": 2, "v": "b"})
    # A later record replaces a buffered one with the same key.
    writer.write({"id": 1, "v": "c"})
    writer.write({"id": 2, "_ab_cdc_deleted_at": "2026-01-01T00:00:00Z"})
    writer.write({"id": 2, "v": "d"})
    writer.flush()

    assert client.requests == [
        (
            "add",
            [
                {"id": 1, "v": "c", PRIMARY_KEY: "1", "_airbyte_generation_id": 3},
                {"id": 2, "v": "b", PRIMARY_KEY: "2", "_airbyte_generation_id": 3},
            ],
        ),
        ("delete", ["2"]),
        ("add", [{"id": 2, "v": "d", PRIMARY_KEY: "2", "_airbyte_generation_id": 3}]),
    ]
    assert writer.pending_tasks == [1, 2, 3]
    assert writer.records_written == 3 and writer.records_deleted == 1


def test_writer_append_batches():
    client = FakeClient()
    writer = StreamWriter(client, "idx", batch_size=2)
    for i in range(5):
        # Append streams don't treat CDC deletions specially.
        writer.write({"id": 1, "_ab_cdc_deleted_at": None if i else "x"})
    writer.flush()

    assert [len(docs) for kind, docs in client.requests] == [2, 2, 1]
    ids = {doc[PRIMARY_KEY] for _, docs in client.requests for doc in docs}
    assert len(ids) == 5
    assert all("_airbyte_generation_id" not in doc for _, docs in client.requests for doc in docs)


def test_with_retry():
    sleeps = []
    calls = []

    def flaky():
        calls.append(1)
        if len(calls) == 1:
            raise MeilisearchCommunicationError("connection reset")
        if len(calls) == 2:
            raise api_error(503)
        return "ok"

    assert with_retry("op", flaky, sleeps.append) == "ok"
    assert sleeps == [1, 2]

    # Errors with the request itself are not retried.
    calls.clear()

    def bad():
        calls.append(1)
        raise api_error(400, "invalid_document_id")

    with pytest.raises(MeilisearchApiError):
        with_retry("op", bad, sleeps.append)
    assert len(calls) == 1

    # Retries give up eventually.
    calls.clear()

    def down():
        calls.append(1)
        raise api_error(502)

    with pytest.raises(MeilisearchApiError):
        with_retry("op", down, lambda _: None)
    assert len(calls) == MAX_ATTEMPTS


def task(uid: int, status: str, **kwargs):
    return SimpleNamespace(uid=uid, status=status, type="documentAdditionOrUpdate", index_uid="idx", error=kwargs.get("error"))


def test_wait_for_tasks():
    sleeps = []
    client = MeiliClient("http://localhost:7700/", "key", sleep=sleeps.append)
    assert client.client.config.url == "http://localhost:7700"

    polls = {uid: 0 for uid in range(150)}

    def get_tasks(params):
        uids = [int(u) for u in params["uids"]]
        assert params["limit"] == len(uids) <= 100
        results = []
        for uid in uids:
            polls[uid] += 1
            results.append(task(uid, "succeeded" if polls[uid] > uid % 3 else "processing"))
        return SimpleNamespace(results=results)

    client.client.get_tasks = get_tasks
    client.wait_for_tasks(range(150))
    # Tasks are polled until they finish, with a growing delay.
    assert sleeps == [0.05, 0.1]
    assert all(polls[uid] == uid % 3 + 1 for uid in polls)


def test_wait_for_tasks_failed():
    client = MeiliClient("http://localhost:7700", None, sleep=lambda _: None)
    client.client.get_tasks = lambda params: SimpleNamespace(
        results=[task(1, "succeeded"), task(2, "failed", error={"message": "bad id", "code": "invalid_document_id"})]
    )
    with pytest.raises(TaskFailedError, match=r"task 2 for index 'idx' failed: bad id \(invalid_document_id\)") as exc:
        client.wait_for_tasks([1, 2])
    assert exc.value.code == "invalid_document_id"

    client.client.get_tasks = lambda params: SimpleNamespace(results=[])
    with pytest.raises(RuntimeError, match="Task 3 was not found"):
        client.wait_for_tasks([3])


def configured_stream(mode: DestinationSyncMode, generation_id=None, minimum_generation_id=None, primary_key=None, namespace=None):
    return ConfiguredAirbyteStream(
        stream=AirbyteStream(name="users", namespace=namespace, json_schema={}, supported_sync_modes=[SyncMode.incremental]),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=mode,
        primary_key=primary_key,
        generation_id=generation_id,
        minimum_generation_id=minimum_generation_id,
    )


def test_stream_index_and_generations():
    assert stream_index(configured_stream(DestinationSyncMode.append, namespace="public")) == "public_users"
    # Without generations, nothing is truncated once the stream completes.
    assert truncation_generation(configured_stream(DestinationSyncMode.overwrite)) is None
    # Overwrites delete every earlier generation, including on the first sync.
    assert truncation_generation(configured_stream(DestinationSyncMode.overwrite, 0, 0)) == 0
    assert truncation_generation(configured_stream(DestinationSyncMode.overwrite, 3, 3)) == 3
    # Refreshes which truncate delete generations below the minimum.
    assert truncation_generation(configured_stream(DestinationSyncMode.append_dedup, 2, 2)) == 2
    assert truncation_generation(configured_stream(DestinationSyncMode.append, 2, 0)) is None


def test_check_unique_indexes():
    def stream(name, namespace=None):
        return configured_stream(DestinationSyncMode.append, namespace=namespace).__class__(
            stream=AirbyteStream(name=name, namespace=namespace, json_schema={}, supported_sync_modes=[SyncMode.incremental]),
            sync_mode=SyncMode.incremental,
            destination_sync_mode=DestinationSyncMode.append,
        )

    check_unique_indexes(ConfiguredAirbyteCatalog(streams=[stream("a"), stream("b"), stream("a", "ns")]))
    for streams in ([stream("a.b"), stream("a_b")], [stream("x", "ns"), stream("ns_x")]):
        with pytest.raises(AirbyteTracedException, match="would both be written to the index"):
            check_unique_indexes(ConfiguredAirbyteCatalog(streams=streams))


def test_writer_cdc_ordering_cases():
    # Delete then re-insert, and insert then delete, of the same key in one
    # batch, with a composite key and a non-ASCII value which is hashed.
    client = FakeClient()
    writer = StreamWriter(client, "idx", batch_size=100, primary_key=[["id"], ["name"]])
    deleted = "2026-01-01T00:00:00Z"
    writer.write({"id": 1, "name": "é", "_ab_cdc_deleted_at": deleted})
    writer.write({"id": 1, "name": "é", "v": 1})
    writer.write({"id": 2, "name": "ü", "v": 2})
    writer.write({"id": 2, "name": "ü", "_ab_cdc_deleted_at": deleted})
    writer.flush()

    id1, id2 = document_id([1, "é"]), document_id([2, "ü"])
    assert id1.startswith("h_") and id2.startswith("h_")
    assert [(kind, [d[PRIMARY_KEY] if isinstance(d, dict) else d for d in docs]) for kind, docs in client.requests] == [
        ("delete", [id1]),
        ("add", [id1, id2]),
        ("delete", [id2]),
    ]


def test_writer_missing_key():
    writer = StreamWriter(FakeClient(), "idx", batch_size=100, primary_key=[["id"]])
    with pytest.raises(ValueError, match="primary key field 'id'"):
        writer.write({"other": 1})


def test_write_emits_state_after_tasks_succeed(mocker):
    events = []
    client = MagicMock()
    client.client = FakeClient().client
    client.enqueue.side_effect = lambda description, fn: (events.append("enqueue"), fn().task_uid)[1]
    client.wait_for_tasks.side_effect = lambda uids: events.append(("wait", list(uids)))
    mocker.patch("destination_meilisearch.destination.get_client", return_value=client)

    catalog = ConfiguredAirbyteCatalog(streams=[configured_stream(DestinationSyncMode.append_dedup, primary_key=[["id"]])])

    def record(i):
        return AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream="users", data={"id": i}, emitted_at=0))

    state = AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(type=AirbyteStateType.LEGACY, data={"cursor": 1}))

    output = DestinationMeilisearch().write({"host": "http://localhost:7700"}, catalog, iter([record(1), record(2), state]))
    for message in output:
        events.append("state")

    # States are held while records keep arriving, and emitted once the records
    # before them have been applied.
    assert events == ["enqueue", ("wait", [1]), "state"]


def test_write_emits_state_immediately_without_pending_records(mocker):
    client = MagicMock()
    client.client = FakeClient().client
    mocker.patch("destination_meilisearch.destination.get_client", return_value=client)
    catalog = ConfiguredAirbyteCatalog(streams=[configured_stream(DestinationSyncMode.append)])
    state = AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(type=AirbyteStateType.LEGACY, data={"cursor": 1}))
    assert len(list(DestinationMeilisearch().write({"host": "http://localhost:7700"}, catalog, iter([state, state])))) == 2


def test_write_checkpoints_once_a_batch_has_arrived(mocker):
    events = []
    client = MagicMock()
    client.client = FakeClient().client
    client.enqueue.side_effect = lambda description, fn: fn().task_uid
    client.wait_for_tasks.side_effect = lambda uids: events.append(("wait", list(uids)))
    mocker.patch("destination_meilisearch.destination.get_client", return_value=client)
    catalog = ConfiguredAirbyteCatalog(streams=[configured_stream(DestinationSyncMode.append)])

    def record(i):
        return AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream="users", data={"id": i}, emitted_at=0))

    def state(i):
        return AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(type=AirbyteStateType.LEGACY, data={"cursor": i}))

    messages = [record(1), state(1), record(2), state(2), record(3), state(3)]
    for message in DestinationMeilisearch().write({"host": "http://localhost:7700", "batch_size": 2}, catalog, iter(messages)):
        events.append(message.state.data["cursor"])
    # The first two states are emitted once two records have arrived, the
    # last one at the end of the input.
    assert events == [("wait", [1]), 1, 2, ("wait", [2]), 3]
    client.ensure_index.assert_called_once_with("users", PRIMARY_KEY)
