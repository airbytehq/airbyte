#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import responses
from source_convex.source import SourceConvex

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


DEPLOYMENT_URL = "https://murky-swan-635.convex.cloud"
CONFIG = {"deployment_url": DEPLOYMENT_URL, "access_key": "test_api_key"}
JSON_SCHEMAS = {
    "messages": {
        "type": "object",
        "properties": {
            "_id": {"type": "string"},
            "_ts": {"type": "integer"},
            "body": {"type": "string"},
        },
    },
}


def _setup_responses():
    responses.add(responses.GET, f"{DEPLOYMENT_URL}/api/json_schemas?deltaSchema=true&format=json", json=JSON_SCHEMAS)
    responses.add(
        responses.GET,
        f"{DEPLOYMENT_URL}/api/list_snapshot?tableName=messages&format=json",
        json={"values": [{"_id": "a", "_ts": 1_000_000_000, "body": "first"}], "cursor": "c1", "snapshot": 5000, "hasMore": True},
    )
    responses.add(
        responses.GET,
        f"{DEPLOYMENT_URL}/api/list_snapshot?tableName=messages&format=json&cursor=c1&snapshot=5000",
        json={"values": [{"_id": "b", "_ts": 2_000_000_000, "body": "second"}], "cursor": "c2", "snapshot": 5000, "hasMore": False},
    )
    responses.add(
        responses.GET,
        f"{DEPLOYMENT_URL}/api/document_deltas?tableName=messages&format=json&cursor=5000",
        json={"values": [{"_id": "a", "_ts": 3_000_000_000, "_deleted": True}], "cursor": 7000, "hasMore": False},
    )


def _stream_state(state_message):
    stream_state = state_message.state.stream.stream_state
    return stream_state if isinstance(stream_state, dict) else dict(stream_state.__dict__)


@responses.activate
def test_read_incremental_emits_records_and_state():
    _setup_responses()
    catalog = CatalogBuilder().with_stream("messages", SyncMode.incremental).build()

    output = read(SourceConvex(), CONFIG, catalog)

    assert not output.errors
    # The CDK omits null values when serializing records, so `_ab_cdc_deleted_at` is absent for non-deleted documents.
    assert [record.record.data for record in output.records] == [
        {
            "_id": "a",
            "_ts": 1_000_000_000,
            "body": "first",
            "_ab_cdc_lsn": 1_000_000_000,
            "_ab_cdc_updated_at": "1970-01-01T00:00:01",
            "_deleted": False,
        },
        {
            "_id": "b",
            "_ts": 2_000_000_000,
            "body": "second",
            "_ab_cdc_lsn": 2_000_000_000,
            "_ab_cdc_updated_at": "1970-01-01T00:00:02",
            "_deleted": False,
        },
        {
            "_id": "a",
            "_ts": 3_000_000_000,
            "_deleted": True,
            "_ab_cdc_lsn": 3_000_000_000,
            "_ab_cdc_updated_at": "1970-01-01T00:00:03",
            "_ab_cdc_deleted_at": "1970-01-01T00:00:03",
        },
    ]
    assert len(responses.calls) == 4
    assert _stream_state(output.state_messages[-1]) == {"snapshot_cursor": "c2", "snapshot_has_more": False, "delta_cursor": 7000}


@responses.activate
def test_read_full_refresh_reads_snapshot_only():
    _setup_responses()
    catalog = CatalogBuilder().with_stream("messages", SyncMode.full_refresh).build()

    output = read(SourceConvex(), CONFIG, catalog)

    assert not output.errors
    assert [record.record.data["body"] for record in output.records] == ["first", "second"]
    assert not any("document_deltas" in call.request.url for call in responses.calls)


@responses.activate
def test_read_incremental_resumes_from_state():
    responses.add(responses.GET, f"{DEPLOYMENT_URL}/api/json_schemas?deltaSchema=true&format=json", json=JSON_SCHEMAS)
    responses.add(
        responses.GET,
        f"{DEPLOYMENT_URL}/api/document_deltas?tableName=messages&format=json&cursor=7000",
        json={"values": [{"_id": "b", "_ts": 8_000_000_000, "body": "updated"}], "cursor": 8000, "hasMore": False},
    )
    catalog = CatalogBuilder().with_stream("messages", SyncMode.incremental).build()
    state = (
        StateBuilder().with_stream_state("messages", {"snapshot_cursor": "c2", "snapshot_has_more": False, "delta_cursor": 7000}).build()
    )

    output = read(SourceConvex(), CONFIG, catalog, state)

    assert not output.errors
    assert [record.record.data["body"] for record in output.records] == ["updated"]
    assert len(responses.calls) == 2
    assert _stream_state(output.state_messages[-1]) == {"snapshot_cursor": "c2", "snapshot_has_more": False, "delta_cursor": 8000}
