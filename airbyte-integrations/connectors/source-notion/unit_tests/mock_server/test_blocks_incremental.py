# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any, Dict, List, Optional

import pytest

from airbyte_cdk.models import ConfiguredAirbyteCatalogSerializer, SyncMode
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


_API = "https://api.notion.com/v1"
_CONFIG = {"start_date": "2020-01-01T00:00:00.000Z", "credentials": {"auth_type": "token", "token": "abcd"}}
_PAGE_EDITED = "2024-01-10T00:00:00.000Z"
_STATE_VALUE = "2024-01-05T00:00:00.000Z"


def _page(page_id: str) -> Dict[str, Any]:
    return {
        "object": "page",
        "id": page_id,
        "created_time": "2023-01-01T00:00:00.000Z",
        "last_edited_time": _PAGE_EDITED,
        "parent": {"type": "workspace", "workspace": True},
        "properties": {},
    }


def _block(block_id: str, last_edited_time: str, has_children: bool = False) -> Dict[str, Any]:
    return {
        "object": "block",
        "id": block_id,
        "parent": {"type": "page_id", "page_id": "page-1"},
        "created_time": "2023-01-01T00:00:00.000Z",
        "last_edited_time": last_edited_time,
        "has_children": has_children,
        "type": "paragraph",
        "paragraph": {"rich_text": []},
    }


def _list(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {"object": "list", "results": results, "next_cursor": None, "has_more": False}


def _register_page_with_nested_blocks(requests_mock) -> None:
    requests_mock.post(f"{_API}/search", json=_list([_page("page-1")]))
    requests_mock.get(
        f"{_API}/blocks/page-1/children?page_size=100",
        json=_list(
            [
                _block("unchanged-top", "2024-01-01T00:00:00.000Z"),
                # An unchanged block whose child was edited: the child is still fetched and emitted.
                _block("unchanged-parent", "2024-01-02T00:00:00.000Z", has_children=True),
                _block("edited-at-state", _STATE_VALUE),
                _block("edited-top", "2024-01-08T00:00:00.000Z"),
            ]
        ),
    )
    requests_mock.get(
        f"{_API}/blocks/unchanged-parent/children?page_size=100",
        json=_list(
            [
                _block("unchanged-child", "2024-01-03T00:00:00.000Z"),
                _block("edited-child", "2024-01-09T00:00:00.000Z"),
            ]
        ),
    )


def _read_blocks(sync_mode: SyncMode, state: Optional[Dict[str, Any]] = None) -> EntrypointOutput:
    catalog = ConfiguredAirbyteCatalogSerializer.load(
        {
            "streams": [
                {
                    "stream": {"name": "blocks", "json_schema": {}, "supported_sync_modes": ["full_refresh", "incremental"]},
                    "sync_mode": sync_mode.value,
                    "destination_sync_mode": "append",
                }
            ]
        }
    )
    state_messages = StateBuilder().with_stream_state("blocks", state).build() if state else StateBuilder().build()
    return read(get_source(_CONFIG, state_messages), config=_CONFIG, catalog=catalog, state=state_messages)


def _emitted_ids(output: EntrypointOutput) -> List[str]:
    return [message.record.data["id"] for message in output.records]


def test_incremental_read_with_state_emits_only_blocks_edited_since_state(requests_mock):
    _register_page_with_nested_blocks(requests_mock)

    output = _read_blocks(
        SyncMode.incremental,
        state={"use_global_cursor": True, "state": {"last_edited_time": _STATE_VALUE}, "lookback_window": 0},
    )

    # Blocks edited exactly at the state value are re-emitted (inclusive lower bound); older blocks, including
    # nested children, are not.
    assert sorted(_emitted_ids(output)) == ["edited-at-state", "edited-child", "edited-top"]
    child_requests = [r for r in requests_mock.request_history if "/blocks/unchanged-parent/children" in r.url]
    assert len(child_requests) == 1
    assert output.most_recent_state.stream_state.__dict__["state"] == {"last_edited_time": "2024-01-09T00:00:00.000000Z"}


@pytest.mark.parametrize("sync_mode", [SyncMode.incremental, SyncMode.full_refresh])
def test_read_without_state_emits_all_blocks_after_start_date(requests_mock, sync_mode):
    _register_page_with_nested_blocks(requests_mock)

    output = _read_blocks(sync_mode)

    assert sorted(_emitted_ids(output)) == [
        "edited-at-state",
        "edited-child",
        "edited-top",
        "unchanged-child",
        "unchanged-parent",
        "unchanged-top",
    ]
