# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from unittest.mock import MagicMock, patch

import pytest

from airbyte_cdk.models import AirbyteMessageSerializer, SyncMode
from airbyte_cdk.sources.declarative.retrievers.simple_retriever import SimpleRetriever
from airbyte_cdk.sources.declarative.types import Record, StreamSlice
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


def _final_cursor(output):
    state = AirbyteMessageSerializer.dump(output.state_messages[-1])["state"]["stream"]["stream_state"]
    assert state["use_global_cursor"] is True
    return state["state"]["last_edited_time"]


def test_blocks_incremental_filters_old_blocks_but_reads_their_children(requests_mock):
    config = {"start_date": "2020-01-01T00:00:00.000Z", "credentials": {"auth_type": "token", "token": "abcd"}}
    cursor = "2024-06-01T00:00:00.000Z"
    newest = "2024-06-03T00:00:00.000000Z"

    def response(records):
        return {"object": "list", "results": records, "has_more": False, "next_cursor": None}

    def block(block_id, edited, has_children=False):
        return {
            "object": "block",
            "id": block_id,
            "type": "paragraph",
            "last_edited_time": edited,
            "has_children": has_children,
            "parent": {"type": "page_id", "page_id": "page-1"},
        }

    requests_mock.post(
        "https://api.notion.com/v1/search",
        json=response([{"object": "page", "id": "page-1", "last_edited_time": newest, "properties": {}}]),
    )
    requests_mock.get(
        "https://api.notion.com/v1/blocks/page-1/children",
        json=response([block("old-parent", "2024-05-01T00:00:00.000Z", True), block("new-block", newest)]),
    )
    children = requests_mock.get(
        "https://api.notion.com/v1/blocks/old-parent/children",
        json=response([block("new-child", "2024-06-02T00:00:00.000Z")]),
    )
    catalog = CatalogBuilder().with_stream("blocks", SyncMode.incremental).build()
    state = StateBuilder().with_stream_state("blocks", {"state": {"last_edited_time": cursor}, "use_global_cursor": True}).build()
    output = read(get_source(config, state), config, catalog, state=state)

    assert not output.errors
    assert [record.record.data["id"] for record in output.records] == ["new-child", "new-block"]
    assert children.call_count == 1
    assert [record.record.data["parent"]["sequence_number"] for record in output.records] == [0, 1]
    assert _final_cursor(output) == newest


@pytest.mark.parametrize("empty", [False, True])
def test_blocks_incremental_all_old(requests_mock, empty):
    config = {"start_date": "2020-01-01T00:00:00.000Z", "credentials": {"auth_type": "token", "token": "abcd"}}
    requests_mock.post(
        "https://api.notion.com/v1/search",
        json={"results": [{"object": "page", "id": "page-1", "last_edited_time": "2024-06-03T00:00:00.000Z", "properties": {}}]},
    )
    requests_mock.get(
        "https://api.notion.com/v1/blocks/page-1/children",
        json={
            "results": []
            if empty
            else [
                {"id": "old-1", "type": "paragraph", "has_children": False, "last_edited_time": "2024-05-01T00:00:00.000Z"},
                {"id": "old-2", "type": "paragraph", "has_children": False, "last_edited_time": "2024-05-02T00:00:00.000Z"},
            ]
        },
    )
    catalog = CatalogBuilder().with_stream("blocks", SyncMode.incremental).build()
    state = (
        StateBuilder()
        .with_stream_state("blocks", {"state": {"last_edited_time": "2024-06-01T00:00:00.000Z"}, "use_global_cursor": True})
        .build()
    )
    output = read(get_source(config, state), config, catalog, state=state)
    assert not output.errors
    assert not output.records
    assert _final_cursor(output) == "2024-06-01T00:00:00.000000Z"


def test_blocks_incremental_two_syncs(requests_mock):
    config = {"start_date": "2020-01-01T00:00:00.000Z", "credentials": {"auth_type": "token", "token": "abcd"}}
    requests_mock.post(
        "https://api.notion.com/v1/search",
        json={"results": [{"object": "page", "id": "page-1", "last_edited_time": "2024-06-03T00:00:00.000Z", "properties": {}}]},
    )
    requests_mock.get(
        "https://api.notion.com/v1/blocks/page-1/children",
        json={
            "results": [
                {"id": "older", "type": "paragraph", "has_children": False, "last_edited_time": "2024-05-01T00:00:00.000Z"},
                {"id": "newest", "type": "paragraph", "has_children": False, "last_edited_time": "2024-06-03T00:00:00.000Z"},
            ]
        },
    )
    catalog = CatalogBuilder().with_stream("blocks", SyncMode.incremental).build()
    first = read(get_source(config), config, catalog)
    assert not first.errors
    assert [record.record.data["id"] for record in first.records] == ["older", "newest"]
    assert _final_cursor(first) == "2024-06-03T00:00:00.000000Z"
    state = [first.state_messages[-1].state]
    second = read(get_source(config, state), config, catalog, state=state)
    assert not second.errors
    # The cursor includes its boundary record in the next sync.
    assert [record.record.data["id"] for record in second.records] == ["newest"]
    assert _final_cursor(second) == "2024-06-03T00:00:00.000000Z"


def test_blocks_without_cursor_filters_nothing(components_module):
    retriever = components_module.BlocksRetriever(
        name="blocks",
        primary_key=["id"],
        requester=MagicMock(),
        record_selector=MagicMock(),
        config={},
        parameters={},
    )
    stream_slice = StreamSlice(partition={}, cursor_slice={})
    record = Record(data={"id": "old", "last_edited_time": "2019-05-01T00:00:00.000Z"}, stream_name="blocks", associated_slice=stream_slice)
    with patch.object(SimpleRetriever, "read_records", return_value=iter([record])):
        assert list(retriever.read_records({}, stream_slice)) == [record]
