# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any, Dict, List, Optional

import pytest

from airbyte_cdk.models import ConfiguredAirbyteCatalogSerializer
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


_BASE_URL = "https://api.notion.com/v1"
_CONFIG = {"start_date": "2020-01-01T00:00:00.000Z", "credentials": {"auth_type": "token", "token": "abcd"}}
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


def _block(block_id: str, last_edited_time: str, has_children: bool = False) -> Dict[str, Any]:
    return {
        "object": "block",
        "id": block_id,
        "parent": {"type": "page_id", "page_id": "page-1"},
        "created_time": "2021-01-01T00:00:00.000Z",
        "last_edited_time": last_edited_time,
        "has_children": has_children,
        "archived": False,
        "in_trash": False,
        "type": "paragraph",
        "paragraph": {"rich_text": []},
    }


def _list(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {"object": "list", "results": results, "has_more": False, "next_cursor": None}


def _mock_api(requests_mock, toggle_child_edited: str, paragraph_edited: str) -> None:
    """
    One page holding three top-level blocks:
      - `toggle` (has children, last edited 2021-06-01) -> child `toggle-child`
      - `old-paragraph` (last edited 2021-06-01)
      - `paragraph` (last edited at `paragraph_edited`)
    Editing a nested block in Notion does not move its parent's `last_edited_time`, so `toggle` stays old.
    """
    page = {"object": "page", "id": "page-1", "last_edited_time": "2024-03-01T00:00:00.000Z", "properties": {}}
    requests_mock.post(f"{_BASE_URL}/search", json=_list([page]))
    requests_mock.get(
        f"{_BASE_URL}/blocks/page-1/children?page_size=100",
        json=_list(
            [
                _block("toggle", "2021-06-01T00:00:00.000Z", has_children=True),
                _block("old-paragraph", "2021-06-01T00:00:00.000Z"),
                _block("paragraph", paragraph_edited),
            ]
        ),
    )
    requests_mock.get(
        f"{_BASE_URL}/blocks/toggle/children?page_size=100",
        json=_list([_block("toggle-child", toggle_child_edited)]),
    )


def _read(state: Optional[List[Any]] = None) -> EntrypointOutput:
    state = state or StateBuilder().build()
    return read(get_source(_CONFIG, state), config=_CONFIG, catalog=_CATALOG, state=state)


def _cursor_value(output: EntrypointOutput) -> str:
    return output.most_recent_state.stream_state.__dict__["state"]["last_edited_time"]


def test_incremental_read_emits_only_blocks_edited_since_state(requests_mock):
    """
    Second sync must emit only blocks edited at or after the saved cursor, including a recently edited child of an
    unchanged parent block, instead of re-emitting every block of every page.
    """
    _mock_api(requests_mock, toggle_child_edited="2023-01-01T00:00:00.000Z", paragraph_edited="2023-01-01T00:00:00.000Z")
    first = _read()

    assert [r.record.data["id"] for r in first.records] == ["toggle-child", "toggle", "old-paragraph", "paragraph"]
    assert _cursor_value(first) == "2023-01-01T00:00:00.000000Z"

    # `paragraph` is unchanged since the first sync and is emitted again because the cursor is inclusive (>=);
    # `toggle-child` was edited since. Blocks last edited in 2021 must not be emitted again.
    requests_mock.reset_mock()
    _mock_api(requests_mock, toggle_child_edited="2024-02-01T00:00:00.000Z", paragraph_edited="2023-01-01T00:00:00.000Z")
    second = _read(StateBuilder().with_stream_state("blocks", first.most_recent_state.stream_state.__dict__).build())

    assert [r.record.data["id"] for r in second.records] == ["toggle-child", "paragraph"]
    assert _cursor_value(second) == "2024-02-01T00:00:00.000000Z"
    # the unchanged parent block is still traversed so its edited child is found
    assert [r.url for r in requests_mock.request_history if r.method == "GET"] == [
        f"{_BASE_URL}/blocks/page-1/children?page_size=100",
        f"{_BASE_URL}/blocks/toggle/children?page_size=100",
    ]
