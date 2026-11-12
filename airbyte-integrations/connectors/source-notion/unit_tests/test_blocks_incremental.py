# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

from airbyte_cdk.models import ConfiguredAirbyteCatalogSerializer
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


# `old-block` below was last edited before this start date, on a page edited after it
_CONFIG = {"start_date": "2021-10-20T00:00:00.000Z", "credentials": {"auth_type": "token", "token": "abcd"}}
_CATALOG = ConfiguredAirbyteCatalogSerializer.load(
    {
        "streams": [
            {
                "stream": {"name": "blocks", "json_schema": {}, "supported_sync_modes": ["full_refresh", "incremental"]},
                "sync_mode": "incremental",
                "destination_sync_mode": "append",
            }
        ]
    }
)


def _list(results):
    return {"object": "list", "results": results, "next_cursor": None, "has_more": False}


def _block(block_id, last_edited_time, has_children=False):
    return {
        "object": "block",
        "id": block_id,
        "parent": {"type": "page_id", "page_id": "page-1"},
        "created_time": "2021-10-01T00:00:00.000Z",
        "last_edited_time": last_edited_time,
        "has_children": has_children,
        "archived": False,
        "in_trash": False,
        "type": "paragraph",
        "paragraph": {"rich_text": [], "color": "default"},
    }


def _mock_notion(requests_mock, page_last_edited_time, page_blocks, child_blocks):
    """page-1 holds `page_blocks`; the block `parent-block` holds `child_blocks`."""
    page = {
        "object": "page",
        "id": "page-1",
        "created_time": "2021-10-01T00:00:00.000Z",
        "last_edited_time": page_last_edited_time,
        "properties": {},
    }
    requests_mock.register_uri("POST", "https://api.notion.com/v1/search", json=_list([page]))
    requests_mock.register_uri("GET", "https://api.notion.com/v1/blocks/page-1/children?page_size=100", json=_list(page_blocks))
    requests_mock.register_uri("GET", "https://api.notion.com/v1/blocks/parent-block/children?page_size=100", json=_list(child_blocks))


def _read_blocks(state):
    return read(get_source(_CONFIG, state), config=_CONFIG, catalog=_CATALOG, state=state)


def _block_requests(requests_mock):
    return [request.url for request in requests_mock.request_history if "/blocks/" in request.url]


def test_second_incremental_read_emits_only_blocks_edited_since_the_previous_state(requests_mock):
    _mock_notion(
        requests_mock,
        page_last_edited_time="2021-11-19T13:33:00.000Z",
        page_blocks=[
            _block("old-block", "2021-10-19T13:33:00.000Z"),
            _block("parent-block", "2021-10-20T13:33:00.000Z", has_children=True),
        ],
        child_blocks=[_block("child-block", "2021-11-19T13:33:00.000Z")],
    )

    first_read = _read_blocks(StateBuilder().with_stream_state("blocks", {}).build())

    # The first sync emits the whole content of the page, including the block that predates the start date.
    assert [record.record.data["id"] for record in first_read.records] == ["old-block", "child-block", "parent-block"]
    first_state = first_read.most_recent_state.stream_state.__dict__
    assert first_state["state"] == {"last_edited_time": "2021-11-19T13:33:00.000000Z"}

    # Between the syncs one nested block is edited and one is added; Notion bumps the page's last_edited_time,
    # but neither `old-block` nor the nested blocks' own parent block changes.
    requests_mock.reset_mock()
    _mock_notion(
        requests_mock,
        page_last_edited_time="2021-12-01T08:00:00.000Z",
        page_blocks=[
            _block("old-block", "2021-10-19T13:33:00.000Z"),
            _block("parent-block", "2021-10-20T13:33:00.000Z", has_children=True),
        ],
        child_blocks=[
            _block("child-block", "2021-12-01T08:00:00.000Z"),
            _block("unchanged-child-block", "2021-11-01T00:00:00.000Z"),
            # edited at exactly the previous cursor value: the cursor is inclusive, so this one repeats
            _block("boundary-child-block", "2021-11-19T13:33:00.000Z"),
        ],
    )

    second_read = _read_blocks(StateBuilder().with_stream_state("blocks", first_state).build())

    # Unchanged blocks are not emitted again, while children of an unchanged parent block are still fetched.
    assert [record.record.data["id"] for record in second_read.records] == ["child-block", "boundary-child-block"]
    assert _block_requests(requests_mock) == [
        "https://api.notion.com/v1/blocks/page-1/children?page_size=100",
        "https://api.notion.com/v1/blocks/parent-block/children?page_size=100",
    ]
    assert second_read.most_recent_state.stream_state.__dict__["state"] == {"last_edited_time": "2021-12-01T08:00:00.000000Z"}
