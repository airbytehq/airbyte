# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from freezegun import freeze_time

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


_CONFIG = {"start_date": "2020-01-01T00:00:00.000Z", "credentials": {"auth_type": "token", "token": "abcd"}}
_OLD = "2024-01-01T00:00:00.000Z"
_STATE = "2024-01-02T00:00:00.000Z"
_NEW = "2024-01-03T00:00:00.000Z"
_BASE_URL = "https://api.notion.com/v1/"


def _response(records):
    return HttpResponse(json.dumps({"object": "list", "results": records, "has_more": False, "next_cursor": None}))


def _block(block_id, edited_time, has_children=False):
    return {
        "object": "block",
        "id": block_id,
        "type": "paragraph",
        "last_edited_time": edited_time,
        "has_children": has_children,
        "parent": {"type": "page_id", "page_id": "page-id"},
    }


def test_incremental_blocks_filters_old_records_and_reads_their_children():
    state = StateBuilder().with_stream_state("blocks", {"state": {"last_edited_time": _STATE}}).build()
    catalog = CatalogBuilder().with_stream("blocks", SyncMode.incremental).build()
    with HttpMocker() as http_mocker:
        http_mocker.post(
            HttpRequest(
                _BASE_URL + "search",
                body={
                    "sort": {"direction": "descending", "timestamp": "last_edited_time"},
                    "filter": {"property": "object", "value": "page"},
                    "page_size": 100,
                },
            ),
            _response([{"object": "page", "id": "page-id", "last_edited_time": _NEW}]),
        )
        http_mocker.get(
            HttpRequest(_BASE_URL + "blocks/page-id/children", query_params={"page_size": 100}),
            _response([_block("old-parent", _OLD, has_children=True), _block("old-block", _OLD), _block("new-block", _NEW)]),
        )
        http_mocker.get(
            HttpRequest(_BASE_URL + "blocks/old-parent/children", query_params={"page_size": 100}),
            _response([_block("new-child", _NEW)]),
        )
        output = read(get_source(_CONFIG, state), _CONFIG, catalog, state=state)

    assert {record.record.data["id"] for record in output.records} == {"new-block", "new-child"}
    assert {record.record.data["id"]: record.record.data["parent"]["sequence_number"] for record in output.records} == {
        "new-block": 2,
        "new-child": 0,
    }
    emitted_state = vars(output.most_recent_state.stream_state)
    assert emitted_state["state"] == {"last_edited_time": "2024-01-03T00:00:00.000000Z"}
    assert emitted_state["states"] == [
        {
            "partition": {"block_id": "page-id", "parent_slice": {}},
            "cursor": {"last_edited_time": "2024-01-03T00:00:00.000000Z"},
        }
    ]


def _read_pages(pages, state, child_edited_times=None, sync_mode=SyncMode.incremental, child_response=None):
    catalog = CatalogBuilder().with_stream("blocks", sync_mode).build()
    with HttpMocker() as http_mocker:
        http_mocker.post(
            HttpRequest(
                _BASE_URL + "search",
                body={
                    "sort": {"direction": "descending", "timestamp": "last_edited_time"},
                    "filter": {"property": "object", "value": "page"},
                    "page_size": 100,
                },
            ),
            _response([{"object": "page", "id": page_id, "last_edited_time": "2024-01-07T00:00:00.000Z"} for page_id in pages]),
        )
        for page_id, blocks in pages.items():
            http_mocker.get(
                HttpRequest(_BASE_URL + f"blocks/{page_id}/children", query_params={"page_size": 100}),
                _response(blocks),
            )
            for block in blocks:
                if block["has_children"]:
                    http_mocker.get(
                        HttpRequest(_BASE_URL + f"blocks/{block['id']}/children", query_params={"page_size": 100}),
                        child_response or _response([_block(block["id"] + "-child", (child_edited_times or {}).get(block["id"], _STATE))]),
                    )
        return read(get_source(_CONFIG, state), _CONFIG, catalog, state=state)


@freeze_time("2024-02-01T00:00:00Z")
def test_blocks_two_syncs_reuse_exact_emitted_state():
    pages = {
        page_id: [
            _block(page_id + "-parent", _OLD, has_children=True),
            _block(page_id + "-leaf", f"2024-01-0{day}T00:00:00.000Z"),
        ]
        for page_id, day in [("page-a", 3), ("page-b", 4), ("page-c", 5)]
    }
    first = _read_pages(pages, [])
    first_state = vars(first.most_recent_state.stream_state)
    assert first_state["state"] == {"last_edited_time": "2024-01-05T00:00:00.000000Z"}

    state = StateBuilder().with_stream_state("blocks", first_state).build()
    pages["page-b"][1]["last_edited_time"] = "2024-01-06T00:00:00.000Z"
    second = _read_pages(pages, state, child_edited_times={"page-b-parent": "2024-01-06T00:00:00.000Z"})
    second_ids = sorted(record.record.data["id"] for record in second.records)
    assert second_ids == ["page-b-leaf", "page-b-parent-child", "page-c-leaf"]
    boundary_records = [
        record.record.data["id"] for record in second.records if record.record.data["last_edited_time"] == "2024-01-05T00:00:00.000Z"
    ]
    assert boundary_records == ["page-c-leaf"]
    assert vars(second.most_recent_state.stream_state)["state"] == {"last_edited_time": "2024-01-06T00:00:00.000000Z"}


def test_blocks_full_refresh_emits_all_siblings_and_children_with_sequence_numbers():
    pages = {"page-id": [_block("parent", _OLD, has_children=True), _block("sibling", _NEW)]}
    output = _read_pages(pages, [], sync_mode=SyncMode.full_refresh)
    assert {record.record.data["id"]: record.record.data["parent"]["sequence_number"] for record in output.records} == {
        "parent-child": 0,
        "parent": 0,
        "sibling": 1,
    }


@pytest.mark.parametrize("child_response", [_response([]), HttpResponse(json.dumps({"object": "error", "code": "object_not_found"}), 404)])
def test_incremental_blocks_handles_empty_or_inaccessible_children(child_response):
    pages = {"page-id": [_block("old-parent", _OLD, has_children=True), _block("new-sibling", _NEW)]}
    state = StateBuilder().with_stream_state("blocks", {"state": {"last_edited_time": _STATE}}).build()
    output = _read_pages(pages, state, child_response=child_response)
    assert [record.record.data["id"] for record in output.records] == ["new-sibling"]
