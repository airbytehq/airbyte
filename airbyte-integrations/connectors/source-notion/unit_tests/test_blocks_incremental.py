# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from datetime import datetime

import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


CONFIG = {"start_date": "2020-01-01T00:00:00.000Z", "credentials": {"auth_type": "token", "token": "abcd"}}
OLD = "2023-01-01T00:00:00.000Z"
BOUNDARY = "2024-01-01T00:00:00.000Z"
NEW = "2024-02-01T00:00:00.000Z"


def block(identifier, edited, children=False):
    return {"object": "block", "id": identifier, "type": "paragraph", "last_edited_time": edited, "has_children": children}


def response(records):
    return {"object": "list", "results": records, "has_more": False, "next_cursor": None}


@pytest.mark.parametrize(
    "stream_state, expected",
    [
        ({"last_edited_time": BOUNDARY}, {"new-child", "new-parent", "boundary"}),
        (
            {"state": {"last_edited_time": BOUNDARY}, "use_global_cursor": True, "lookback_window": 0, "parent_state": {}},
            {"new-child", "new-parent", "boundary"},
        ),
        (
            {"states": [{"partition": {"block_id": "page-1", "parent_slice": {}}, "cursor": {"last_edited_time": BOUNDARY}}]},
            {"new-child", "new-parent", "boundary"},
        ),
        ({}, {"old-parent", "new-child", "new-parent", "old-child", "boundary"}),
    ],
)
def test_incremental_blocks_traverses_filtered_parents(requests_mock, stream_state, expected):
    requests_mock.post(
        "https://api.notion.com/v1/search",
        json=response([{"object": "page", "id": "page-1", "last_edited_time": NEW, "properties": {}}]),
    )
    requests_mock.get(
        "https://api.notion.com/v1/blocks/page-1/children",
        json=response(
            [
                block("old-parent", OLD, True),
                block("new-parent", NEW, True),
                block("boundary", BOUNDARY),
                block("before-start", "2019-01-01T00:00:00.000Z"),
            ]
        ),
    )
    old_children = requests_mock.get(
        "https://api.notion.com/v1/blocks/old-parent/children", json=response([block("new-child", NEW)])
    )
    new_children = requests_mock.get(
        "https://api.notion.com/v1/blocks/new-parent/children", json=response([block("old-child", OLD)])
    )
    state = StateBuilder().with_stream_state("blocks", stream_state).build()
    catalog = CatalogBuilder().with_stream("blocks", SyncMode.incremental).build()
    output = read(get_source(CONFIG, state), CONFIG, catalog, state=state)

    assert not output.errors
    assert old_children.call_count == new_children.call_count == 1
    assert sorted(record.record.data["id"] for record in output.records) == sorted(expected)
    emitted_state = output.most_recent_state.stream_state.__dict__
    cursor_state = emitted_state.get("state") or (
        emitted_state["states"][0]["cursor"] if "states" in emitted_state else emitted_state
    )
    cursor = cursor_state["last_edited_time"]
    assert datetime.fromisoformat(cursor) == datetime.fromisoformat(NEW)


@pytest.mark.parametrize("status", [200, 404])
def test_incremental_blocks_empty_or_inaccessible(requests_mock, status):
    requests_mock.post(
        "https://api.notion.com/v1/search",
        json=response([{"object": "page", "id": "page-1", "last_edited_time": NEW, "properties": {}}]),
    )
    requests_mock.get("https://api.notion.com/v1/blocks/page-1/children", status_code=status, json=response([]))
    state = StateBuilder().with_stream_state("blocks", {"last_edited_time": BOUNDARY}).build()
    output = read(
        get_source(CONFIG, state), CONFIG, CatalogBuilder().with_stream("blocks", SyncMode.incremental).build(), state=state
    )
    assert not output.errors
    assert not output.records
    emitted_state = output.most_recent_state.stream_state.__dict__
    cursor = emitted_state.get("state", emitted_state)["last_edited_time"]
    assert datetime.fromisoformat(cursor) == datetime.fromisoformat(BOUNDARY)
