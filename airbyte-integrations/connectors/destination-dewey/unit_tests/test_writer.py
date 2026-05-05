#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#
"""Unit tests for the Dewey destination writer.

We test against a stubbed DeweyClient so these tests run offline.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Mapping, Optional
from unittest.mock import MagicMock

import pytest
from destination_dewey.client import (
    METADATA_NAMESPACE_FIELD,
    METADATA_PK_FIELD,
    METADATA_STREAM_FIELD,
    PK_TAG_PREFIX,
    STREAM_TAG_PREFIX,
)
from destination_dewey.writer import DeweyWriter

from airbyte_cdk.models import (
    AirbyteRecordMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    SyncMode,
)


STREAM_NAME = "articles"
NS = "default"
STREAM_ID = f"{NS}__{STREAM_NAME}"


def _make_catalog(sync_mode: DestinationSyncMode, *, primary_key: Optional[List[List[str]]] = None) -> ConfiguredAirbyteCatalog:
    return ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(
                    name=STREAM_NAME,
                    namespace=NS,
                    json_schema={"type": "object"},
                    supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental],
                ),
                primary_key=primary_key or [["id"]],
                sync_mode=SyncMode.incremental,
                destination_sync_mode=sync_mode,
            )
        ]
    )


def _record(data: Dict[str, Any]) -> AirbyteRecordMessage:
    return AirbyteRecordMessage(stream=STREAM_NAME, namespace=NS, data=data, emitted_at=0)


def _make_writer(
    sync_mode: DestinationSyncMode,
    *,
    text_fields: Optional[List[str]] = None,
    metadata_fields: Optional[List[str]] = None,
    title_field: str = "",
    flush_interval: int = 100,
    primary_key: Optional[List[List[str]]] = None,
):
    client = MagicMock()
    client.get_collection.return_value = {"id": "col_test", "name": "test"}
    writer = DeweyWriter(
        client=client,
        catalog=_make_catalog(sync_mode, primary_key=primary_key),
        stream_collections={STREAM_ID: "col_test"},
        auto_create_collections=False,
        text_fields=text_fields or [],
        title_field=title_field,
        metadata_fields=metadata_fields or [],
        flush_interval=flush_interval,
        parallelize=False,
    )
    return writer, client


# ---- queue + flush ---------------------------------------------------------------


def test_queue_and_flush_uploads_full_record_when_no_text_fields():
    writer, client = _make_writer(DestinationSyncMode.append)
    writer.queue(_record({"id": 1, "title": "Hi", "body": "world"}))
    writer.flush()

    client.upload_documents.assert_called_once()
    uploads = client.upload_documents.call_args.args[0]
    assert len(uploads) == 1
    upload = uploads[0]
    assert upload["collection_id"] == "col_test"
    assert upload["content_type"] == "application/json"
    assert json.loads(upload["content"]) == {"id": 1, "title": "Hi", "body": "world"}


def test_text_fields_projection_drops_other_keys():
    writer, client = _make_writer(DestinationSyncMode.append, text_fields=["title", "body"])
    writer.queue(_record({"id": 1, "title": "Hi", "body": "hello", "internal_id": "x"}))
    writer.flush()
    upload = client.upload_documents.call_args.args[0][0]
    payload = json.loads(upload["content"])
    assert payload == {"title": "Hi", "body": "hello"}


def test_tags_include_stream_and_pk():
    writer, client = _make_writer(DestinationSyncMode.append)
    writer.queue(_record({"id": 7, "title": "Hi"}))
    writer.flush()
    upload = client.upload_documents.call_args.args[0][0]
    assert f"{STREAM_TAG_PREFIX}{STREAM_ID}" in upload["tags"]
    assert any(t.startswith(PK_TAG_PREFIX) for t in upload["tags"])


def test_metadata_includes_airbyte_internal_fields():
    writer, client = _make_writer(DestinationSyncMode.append, metadata_fields=["author"])
    writer.queue(_record({"id": 7, "title": "Hi", "author": "ari"}))
    writer.flush()
    upload = client.upload_documents.call_args.args[0][0]
    metadata = upload["metadata"]
    assert metadata[METADATA_STREAM_FIELD] == STREAM_ID
    assert metadata[METADATA_NAMESPACE_FIELD] == NS
    assert metadata[METADATA_PK_FIELD] == "7"
    assert metadata["author"] == "ari"


def test_default_metadata_drops_complex_values():
    writer, client = _make_writer(DestinationSyncMode.append)
    writer.queue(_record({"id": 1, "title": "Hi", "tags": ["a", "b"], "nested": {"x": 1}}))
    writer.flush()
    metadata = client.upload_documents.call_args.args[0][0]["metadata"]
    assert "tags" not in metadata  # list, dropped
    assert "nested" not in metadata  # dict, dropped
    assert metadata["title"] == "Hi"


def test_flush_interval_triggers_auto_flush():
    writer, client = _make_writer(DestinationSyncMode.append, flush_interval=2)
    writer.queue(_record({"id": 1, "title": "a"}))
    writer.queue(_record({"id": 2, "title": "b"}))
    # Auto-flush already happened; explicit flush is a no-op.
    writer.flush()
    assert client.upload_documents.call_count == 1
    uploads = client.upload_documents.call_args.args[0]
    assert len(uploads) == 2


def test_filename_uses_title_when_set():
    writer, client = _make_writer(DestinationSyncMode.append, title_field="title")
    writer.queue(_record({"id": 1, "title": "Hello World!"}))
    writer.flush()
    upload = client.upload_documents.call_args.args[0][0]
    assert upload["filename"].endswith(".json")
    assert "Hello-World" in upload["filename"]


def test_filename_falls_back_to_primary_key():
    writer, client = _make_writer(DestinationSyncMode.append)
    writer.queue(_record({"id": 42}))
    writer.flush()
    upload = client.upload_documents.call_args.args[0][0]
    assert upload["filename"] == "42.json"


def test_unmapped_stream_records_are_skipped():
    writer, client = _make_writer(DestinationSyncMode.append)
    other = AirbyteRecordMessage(stream="not_in_catalog", namespace=NS, data={"x": 1}, emitted_at=0)
    writer.queue(other)
    writer.flush()
    client.upload_documents.assert_not_called()


# ---- overwrite -------------------------------------------------------------------


def test_overwrite_deletes_only_records_with_stream_tag():
    writer, client = _make_writer(DestinationSyncMode.overwrite)
    client.find_document_ids_by_tag.return_value = ["doc_1", "doc_2"]
    writer.delete_streams_to_overwrite()
    client.find_document_ids_by_tag.assert_called_once_with("col_test", f"{STREAM_TAG_PREFIX}{STREAM_ID}")
    client.delete_documents.assert_called_once_with("col_test", ["doc_1", "doc_2"])


def test_overwrite_skips_delete_when_no_matching_docs():
    writer, client = _make_writer(DestinationSyncMode.overwrite)
    client.find_document_ids_by_tag.return_value = []
    writer.delete_streams_to_overwrite()
    client.delete_documents.assert_not_called()


def test_overwrite_does_nothing_for_append_streams():
    writer, client = _make_writer(DestinationSyncMode.append)
    writer.delete_streams_to_overwrite()
    client.find_document_ids_by_tag.assert_not_called()
    client.delete_documents.assert_not_called()


# ---- append_dedup ----------------------------------------------------------------


def test_dedup_deletes_prior_versions_before_upload():
    writer, client = _make_writer(DestinationSyncMode.append_dedup)
    client.find_document_ids_by_tag.return_value = ["old_doc_id"]
    writer.queue(_record({"id": 7, "title": "new"}))
    writer.flush()
    # delete_documents called with the prior id, then upload_documents with the new content.
    client.delete_documents.assert_called_once_with("col_test", ["old_doc_id"])
    client.upload_documents.assert_called_once()


def test_dedup_skips_delete_when_record_lacks_pk():
    writer, client = _make_writer(DestinationSyncMode.append_dedup, primary_key=[])
    writer.queue(_record({"title": "no pk here"}))
    writer.flush()
    client.delete_documents.assert_not_called()


# ---- collection resolution -------------------------------------------------------


def test_resolve_collections_validates_existing_id():
    writer, client = _make_writer(DestinationSyncMode.append)
    writer.resolve_collections()
    client.get_collection.assert_called_once_with("col_test")


def test_resolve_collections_raises_when_missing_and_auto_disabled():
    client = MagicMock()
    writer = DeweyWriter(
        client=client,
        catalog=_make_catalog(DestinationSyncMode.append),
        stream_collections={},
        auto_create_collections=False,
        text_fields=[],
        title_field="",
        metadata_fields=[],
        flush_interval=10,
        parallelize=False,
    )
    with pytest.raises(Exception) as excinfo:
        writer.resolve_collections()
    assert STREAM_ID in str(excinfo.value)


def test_resolve_collections_auto_creates_when_enabled():
    client = MagicMock()
    client.create_collection.return_value = {"id": "col_new", "name": "x"}
    writer = DeweyWriter(
        client=client,
        catalog=_make_catalog(DestinationSyncMode.append),
        stream_collections={},
        auto_create_collections=True,
        text_fields=[],
        title_field="",
        metadata_fields=[],
        flush_interval=10,
        parallelize=False,
    )
    writer.resolve_collections()
    client.create_collection.assert_called_once_with(name=f"airbyte_{STREAM_ID}")
    # Subsequent queues should route to the auto-created collection.
    writer.queue(_record({"id": 1, "title": "x"}))
    writer.flush()
    assert client.upload_documents.call_args.args[0][0]["collection_id"] == "col_new"
