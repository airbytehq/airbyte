#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock, patch

import pytest
from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteStateMessage,
    AirbyteStateType,
    AirbyteStreamState,
    DestinationSyncMode,
    StreamDescriptor,
    Type,
)

from destination_meilisearch.destination import DestinationMeilisearch, resolve_primary_key, sanitize_index_name
from destination_meilisearch.writer import (
    ID_HASH,
    ID_NATURAL,
    ID_RANDOM,
    INTERNAL_PK_FIELD,
    MeiliWriter,
)


def _stream(sync_mode, primary_key):
    stream = MagicMock()
    stream.destination_sync_mode = sync_mode
    stream.primary_key = primary_key
    return stream


# ---- index name sanitization ----


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("users", "users"),
        ("my stream", "my_stream"),
        ("schema.table", "schema_table"),
        ("a/b-c_1", "a_b-c_1"),
    ],
)
def test_sanitize_index_name(raw, expected):
    assert sanitize_index_name(raw) == expected


# ---- primary key resolution ----


def test_resolve_single_top_level_key_is_natural():
    pk, mode, paths = resolve_primary_key(_stream(DestinationSyncMode.append_dedup, [["id"]]))
    assert (pk, mode) == ("id", ID_NATURAL)
    assert paths == [["id"]]


def test_resolve_append_always_random_even_with_key():
    pk, mode, paths = resolve_primary_key(_stream(DestinationSyncMode.append, [["id"]]))
    assert (pk, mode, paths) == (INTERNAL_PK_FIELD, ID_RANDOM, [])


def test_resolve_composite_key_is_hash():
    pk, mode, paths = resolve_primary_key(_stream(DestinationSyncMode.append_dedup, [["a"], ["b"]]))
    assert (pk, mode) == (INTERNAL_PK_FIELD, ID_HASH)
    assert paths == [["a"], ["b"]]


def test_resolve_nested_key_is_hash():
    pk, mode, _ = resolve_primary_key(_stream(DestinationSyncMode.append_dedup, [["nested", "id"]]))
    assert (pk, mode) == (INTERNAL_PK_FIELD, ID_HASH)


def test_resolve_no_key_is_random():
    pk, mode, paths = resolve_primary_key(_stream(DestinationSyncMode.overwrite, None))
    assert (pk, mode, paths) == (INTERNAL_PK_FIELD, ID_RANDOM, [])


# ---- writer id preparation ----


def _writer(id_mode, key_paths=None, merge=False, batch_size=1000, primary_key="id"):
    return MeiliWriter(
        client=MagicMock(),
        index_name="idx",
        primary_key=primary_key,
        id_mode=id_mode,
        key_paths=key_paths or [],
        merge=merge,
        batch_size=batch_size,
    )


def test_prepare_natural_passes_through():
    writer = _writer(ID_NATURAL)
    assert writer._prepare({"id": 7, "name": "x"}) == {"id": 7, "name": "x"}


def test_prepare_random_injects_unique_ids():
    writer = _writer(ID_RANDOM, primary_key=INTERNAL_PK_FIELD)
    a = writer._prepare({"name": "x"})
    b = writer._prepare({"name": "x"})
    assert a[INTERNAL_PK_FIELD] != b[INTERNAL_PK_FIELD]


def test_prepare_hash_is_deterministic():
    writer = _writer(ID_HASH, key_paths=[["a"], ["b"]], primary_key=INTERNAL_PK_FIELD)
    first = writer._prepare({"a": 1, "b": 2})[INTERNAL_PK_FIELD]
    second = writer._prepare({"a": 1, "b": 2})[INTERNAL_PK_FIELD]
    different = writer._prepare({"a": 1, "b": 3})[INTERNAL_PK_FIELD]
    assert first == second
    assert first != different


def test_prepare_hash_nested_path():
    writer = _writer(ID_HASH, key_paths=[["nested", "id"]], primary_key=INTERNAL_PK_FIELD)
    assert INTERNAL_PK_FIELD in writer._prepare({"nested": {"id": 5}})


def test_prepare_hash_missing_key_raises():
    writer = _writer(ID_HASH, key_paths=[["missing"]], primary_key=INTERNAL_PK_FIELD)
    with pytest.raises(ValueError):
        writer._prepare({"a": 1})


def test_prepare_hash_null_key_raises():
    writer = _writer(ID_HASH, key_paths=[["a"]], primary_key=INTERNAL_PK_FIELD)
    with pytest.raises(ValueError):
        writer._prepare({"a": None})


# ---- writer flush behavior ----


def _success_task():
    info = MagicMock()
    info.task_uid = 1
    return info


def _flush_client():
    client = MagicMock()
    index = client.index.return_value
    index.add_documents.return_value = _success_task()
    index.update_documents.return_value = _success_task()
    result = MagicMock()
    result.status = "succeeded"
    client.wait_for_task.return_value = result
    return client, index


def test_flush_auto_triggers_on_batch_size():
    client, index = _flush_client()
    writer = MeiliWriter(client, "idx", "id", ID_NATURAL, [], merge=False, batch_size=2)
    writer.queue_write_operation({"id": 1})
    index.add_documents.assert_not_called()
    writer.queue_write_operation({"id": 2})  # reaches batch size -> flush
    index.add_documents.assert_called_once()
    assert writer._buffer == []


def test_flush_uses_add_documents_when_replace():
    client, index = _flush_client()
    writer = MeiliWriter(client, "idx", "id", ID_NATURAL, [], merge=False, batch_size=1000)
    writer.queue_write_operation({"id": 1})
    writer.flush()
    index.add_documents.assert_called_once()
    index.update_documents.assert_not_called()


def test_flush_uses_update_documents_when_merge():
    client, index = _flush_client()
    writer = MeiliWriter(client, "idx", "id", ID_NATURAL, [], merge=True, batch_size=1000)
    writer.queue_write_operation({"id": 1})
    writer.flush()
    index.update_documents.assert_called_once()
    index.add_documents.assert_not_called()


def test_flush_passes_primary_key():
    client, index = _flush_client()
    writer = MeiliWriter(client, "idx", "ref", ID_NATURAL, [], merge=False, batch_size=1000)
    writer.queue_write_operation({"ref": "abc"})
    writer.flush()
    args, _ = index.add_documents.call_args
    assert args[1] == "ref"


def test_flush_empty_is_noop():
    client, index = _flush_client()
    writer = MeiliWriter(client, "idx", "id", ID_NATURAL, [], merge=False, batch_size=1000)
    writer.flush()
    index.add_documents.assert_not_called()


def test_flush_raises_on_failed_task():
    client, index = _flush_client()
    failed = MagicMock()
    failed.status = "failed"
    client.wait_for_task.return_value = failed
    writer = MeiliWriter(client, "idx", "id", ID_NATURAL, [], merge=False, batch_size=1000)
    writer.queue_write_operation({"id": 1})
    with pytest.raises(RuntimeError):
        writer.flush()


# ---- natural key validation ----


@pytest.mark.parametrize("value", [7, 0, -3, "abc", "A-b_1", "0"])
def test_natural_key_valid_values_pass(value):
    writer = _writer(ID_NATURAL)
    assert writer._prepare({"id": value})["id"] == value


@pytest.mark.parametrize("value", ["user@example.com", "a b", "a.b", "", None, True, 1.5, {"x": 1}])
def test_natural_key_invalid_values_raise(value):
    writer = _writer(ID_NATURAL)
    with pytest.raises(ValueError, match="not a valid"):
        writer._prepare({"id": value})


def test_natural_key_missing_field_raises():
    writer = _writer(ID_NATURAL)
    with pytest.raises(ValueError, match="missing primary key"):
        writer._prepare({"name": "x"})


# ---- write() orchestration ----


def _configured_stream(name, sync_mode=DestinationSyncMode.append_dedup, primary_key=None):
    stream = MagicMock()
    stream.stream.name = name
    stream.destination_sync_mode = sync_mode
    stream.primary_key = primary_key if primary_key is not None else [["id"]]
    return stream


def _catalog(*streams):
    catalog = MagicMock()
    catalog.streams = list(streams)
    return catalog


@patch("destination_meilisearch.destination.get_client")
def test_write_rejects_colliding_index_names(mock_get_client):
    catalog = _catalog(_configured_stream("user.events"), _configured_stream("user events"))
    with pytest.raises(ValueError, match="both map to Meilisearch index"):
        list(DestinationMeilisearch().write({"host": "h"}, catalog, []))


@patch("destination_meilisearch.destination.get_client")
def test_write_rejects_primary_key_mismatch_with_existing_index(mock_get_client):
    mock_get_client.return_value.get_index.return_value.primary_key = "_ab_pk"
    catalog = _catalog(_configured_stream("movies"))
    with pytest.raises(ValueError, match="already has primary key '_ab_pk'"):
        list(DestinationMeilisearch().write({"host": "h"}, catalog, []))


def _state_message(name):
    return AirbyteMessage(
        type=Type.STATE,
        state=AirbyteStateMessage(
            type=AirbyteStateType.STREAM,
            stream=AirbyteStreamState(stream_descriptor=StreamDescriptor(name=name)),
        ),
    )


@patch("destination_meilisearch.destination.MeiliWriter")
@patch("destination_meilisearch.destination.get_client")
def test_stream_state_flushes_only_that_stream(mock_get_client, mock_writer_cls):
    mock_get_client.return_value.get_index.return_value.primary_key = None
    writer_a, writer_b = MagicMock(), MagicMock()
    mock_writer_cls.side_effect = [writer_a, writer_b]
    catalog = _catalog(_configured_stream("a"), _configured_stream("b"))

    list(DestinationMeilisearch().write({"host": "h"}, catalog, [_state_message("a")]))

    # stream-scoped state flushes only 'a'; the end-of-input flush hits both.
    assert writer_a.flush.call_count == 2
    assert writer_b.flush.call_count == 1
