#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
from destination_vectara.writer import VectaraWriter

from airbyte_cdk.models import (
    AirbyteRecordMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    SyncMode,
)


@pytest.fixture(autouse=True)
def reset_write_buffer():
    VectaraWriter.write_buffer.clear()
    yield
    VectaraWriter.write_buffer.clear()


def make_record(data):
    return AirbyteRecordMessage(data=data, stream="users", namespace="tenant", emitted_at=0)


def make_stream(name="users", destination_sync_mode=DestinationSyncMode.overwrite, primary_key=None):
    return ConfiguredAirbyteStream(
        stream=AirbyteStream(
            name=name,
            namespace="tenant",
            json_schema={},
            supported_sync_modes=[SyncMode.full_refresh],
        ),
        sync_mode=SyncMode.full_refresh,
        destination_sync_mode=destination_sync_mode,
        primary_key=primary_key,
    )


def make_catalog(*streams):
    return ConfiguredAirbyteCatalog(streams=list(streams))


def make_writer(text_fields=None, title_field=None, metadata_fields=None, catalog=None):
    return VectaraWriter(
        client=MagicMock(),
        text_fields=text_fields,
        title_field=title_field,
        metadata_fields=metadata_fields,
        catalog=catalog or make_catalog(make_stream()),
    )


def test_extract_relevant_fields_supports_nested_paths_and_wildcards():
    writer = make_writer()
    record = make_record({"user": {"name": "Ada"}, "users": [{"name": "Ada"}, {"name": "Grace"}]})

    assert writer._extract_relevant_fields(record, ["user.name", "users.*.name", "missing"]) == {
        "user.name": "Ada",
        "users.*.name": ["Ada", "Grace"],
    }


def test_extract_relevant_fields_without_fields_returns_whole_record():
    data = {"id": 1, "text": "hello"}
    writer = make_writer()

    assert writer._extract_relevant_fields(make_record(data), []) == data


def test_get_document_title_supports_nested_path():
    writer = make_writer(title_field="user.name")

    assert writer._get_document_title(make_record({"user": {"name": "Ada"}})) == "Ada"


def test_get_document_title_falls_back_to_untitled():
    writer = make_writer(title_field="missing")

    assert writer._get_document_title(make_record({"user": {"name": "Ada"}})) == "Untitled"


def test_get_record_primary_key_handles_composite_key_with_missing_field():
    catalog = make_catalog(make_stream(primary_key=[["id"], ["nested", "key"]]))
    writer = make_writer(catalog=catalog)

    assert writer._get_record_primary_key(make_record({"id": 42, "nested": {}})) == "tenant_users_42___not_found__"


def test_delete_streams_to_overwrite_deletes_only_overwrite_streams():
    overwrite_stream = make_stream(name="overwrite", destination_sync_mode=DestinationSyncMode.overwrite)
    append_stream = make_stream(name="append", destination_sync_mode=DestinationSyncMode.append)
    catalog = make_catalog(overwrite_stream, append_stream)
    writer = make_writer(catalog=catalog)

    writer.delete_streams_to_overwrite(catalog)

    writer.client.delete_doc_by_metadata.assert_called_once_with(
        metadata_field_name="_ab_stream", metadata_field_values=["tenant_overwrite"]
    )
