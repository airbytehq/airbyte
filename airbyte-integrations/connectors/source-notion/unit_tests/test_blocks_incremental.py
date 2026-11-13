# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest

from airbyte_cdk.models import AirbyteStateMessageSerializer, ConfiguredAirbyteCatalogSerializer
from airbyte_cdk.test.entrypoint_wrapper import read
from unit_tests.conftest import get_source


CONFIG = {"start_date": "2020-01-01T00:00:00.000Z", "credentials": {"auth_type": "token", "token": "abcd"}}
OLD = "2021-01-01T00:00:00.000Z"
NEW = "2026-01-01T00:00:00.000Z"
CURSOR = "2025-01-01T00:00:00.000Z"
FINAL_CURSOR = "2026-01-01T00:00:00.000000Z"
BASE_URL = "https://api.notion.com/v1/"


def _block(block_id, edited, has_children=False, block_type="paragraph"):
    return {
        "id": block_id,
        "last_edited_time": edited,
        "has_children": has_children,
        "type": block_type,
        "parent": {"type": "page_id", "page_id": "page-new"},
    }


def _response(records):
    return {"object": "list", "results": records, "next_cursor": None, "has_more": False}


def _read(sync_mode="incremental", state=None):
    catalog = ConfiguredAirbyteCatalogSerializer.load(
        {
            "streams": [
                {
                    "stream": {"name": "blocks", "json_schema": {}, "supported_sync_modes": ["full_refresh", "incremental"]},
                    "sync_mode": sync_mode,
                    "destination_sync_mode": "append",
                    "cursor_field": ["last_edited_time"],
                }
            ]
        }
    )
    output = read(get_source(CONFIG, state), config=CONFIG, catalog=catalog, state=state)
    output.raise_if_errors()
    return output


@pytest.fixture(params=["two-pages", "nested"])
def blocks_scenario(request, requests_mock):
    if request.param == "two-pages":
        pages = [("page-old", OLD), ("page-new", NEW)]
        children = {
            page_id: [_block(page_id + "-old", OLD), _block(page_id + "-new", NEW)]
            + [_block(block_type, NEW, block_type=block_type) for block_type in ("child_page", "child_database", "ai_block")]
            for page_id, _ in pages
        }
        incremental_ids = {"page-old-new", "page-new-new"}
        all_ids = {"page-old-old", "page-old-new", "page-new-old", "page-new-new"}
        sequence_numbers = {"page-old-new": 1, "page-new-new": 1}
    else:
        pages = [("page-new", NEW)]
        children = {
            "page-new": [_block("parent-old", OLD, True), _block("parent-new", NEW, True)],
            "parent-old": [_block("child-new", NEW)],
            "parent-new": [_block("child-old", OLD)],
        }
        incremental_ids = {"child-new", "parent-new"}
        all_ids = {"child-new", "parent-old", "child-old", "parent-new"}
        sequence_numbers = {"child-new": 0, "parent-new": 1}
    requests_mock.post(
        BASE_URL + "search",
        json=_response([{"id": page_id, "object": "page", "last_edited_time": edited, "properties": {}} for page_id, edited in pages]),
    )
    for parent_id, records in children.items():
        requests_mock.get(BASE_URL + f"blocks/{parent_id}/children", json=_response(records))
    return (
        incremental_ids,
        all_ids,
        sequence_numbers,
        sorted(BASE_URL + f"blocks/{parent_id}/children?page_size=100" for parent_id in children),
    )


def _children_requests(requests_mock):
    return sorted(request.url for request in requests_mock.request_history if request.method == "GET")


def test_blocks_incremental_state_replay(requests_mock, blocks_scenario):
    incremental_ids, all_ids, sequence_numbers, expected_requests = blocks_scenario
    first = _read()
    first_ids = [message.record.data["id"] for message in first.records]
    assert sorted(first_ids) == sorted(all_ids)
    assert _children_requests(requests_mock) == expected_requests
    state = AirbyteStateMessageSerializer.dump(first.state_messages[-1].state)
    assert state["stream"]["stream_state"]["state"]["last_edited_time"] == FINAL_CURSOR
    state["stream"]["stream_state"]["state"]["last_edited_time"] = CURSOR
    requests_mock.reset_mock()

    second = _read(state=[AirbyteStateMessageSerializer.load(state)])
    assert sorted(message.record.data["id"] for message in second.records) == sorted(incremental_ids)
    assert _children_requests(requests_mock) == expected_requests
    assert {message.record.data["id"]: message.record.data["parent"]["sequence_number"] for message in second.records} == sequence_numbers
    final_state = AirbyteStateMessageSerializer.dump(second.state_messages[-1].state)
    assert final_state["stream"]["stream_state"]["state"]["last_edited_time"] == FINAL_CURSOR


def test_blocks_full_refresh(requests_mock, blocks_scenario):
    _, all_ids, _, expected_requests = blocks_scenario
    output = _read(sync_mode="full_refresh")
    assert sorted(message.record.data["id"] for message in output.records) == sorted(all_ids)
    assert _children_requests(requests_mock) == expected_requests


@pytest.mark.parametrize("status_code", [200, 404])
def test_blocks_empty_or_missing_children(requests_mock, status_code):
    requests_mock.post(BASE_URL + "search", json=_response([{"id": "page-new", "last_edited_time": NEW, "properties": {}}]))
    requests_mock.get(BASE_URL + "blocks/page-new/children", status_code=status_code, json=_response([]))
    output = _read()
    assert output.records == []
    assert _children_requests(requests_mock) == [BASE_URL + "blocks/page-new/children?page_size=100"]
