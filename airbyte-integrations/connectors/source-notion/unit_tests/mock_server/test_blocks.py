# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any, Dict, List, Optional

import pytest

from airbyte_cdk.models import ConfiguredAirbyteCatalogSerializer
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


_CONFIG = {"start_date": "2020-01-01T00:00:00.000Z", "credentials": {"auth_type": "token", "token": "abcd"}}
_STATE_CURSOR = "2025-01-01T00:00:00.000Z"
_OLD = "2024-01-01T00:00:00.000Z"
_NEW = "2025-06-01T00:00:00.000Z"


def _page(page_id: str, last_edited_time: str) -> Dict[str, Any]:
    return {
        "object": "page",
        "id": page_id,
        "created_time": last_edited_time,
        "last_edited_time": last_edited_time,
        "parent": {"type": "workspace", "workspace": True},
        "properties": {},
    }


def _block(block_id: str, parent_id: str, last_edited_time: str, has_children: bool = False) -> Dict[str, Any]:
    return {
        "object": "block",
        "id": block_id,
        "parent": {"type": "page_id", "page_id": parent_id},
        "created_time": last_edited_time,
        "last_edited_time": last_edited_time,
        "has_children": has_children,
        "type": "paragraph",
        "paragraph": {"rich_text": []},
    }


def _list(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {"object": "list", "results": results, "has_more": False, "next_cursor": None}


def _read_blocks(state: Optional[Dict[str, Any]]):
    catalog = ConfiguredAirbyteCatalogSerializer.load(
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
    built_state = StateBuilder().with_stream_state("blocks", state).build() if state else StateBuilder().build()
    return read(get_source(_CONFIG, built_state), config=_CONFIG, catalog=catalog, state=built_state)


@pytest.fixture
def notion_api(requests_mock):
    requests_mock.post("https://api.notion.com/v1/search", json=_list([_page("page-old", _OLD), _page("page-new", _NEW)]))
    requests_mock.get("https://api.notion.com/v1/blocks/page-old/children", json=_list([_block("old-leaf-1", "page-old", _OLD)]))
    requests_mock.get(
        "https://api.notion.com/v1/blocks/page-new/children",
        json=_list(
            [
                _block("old-leaf-2", "page-new", _OLD),
                _block("new-leaf", "page-new", _NEW),
                _block("old-toggle", "page-new", _OLD, has_children=True),
            ]
        ),
    )
    requests_mock.get(
        "https://api.notion.com/v1/blocks/old-toggle/children",
        json=_list([_block("old-nested", "old-toggle", _OLD), _block("new-nested", "old-toggle", _NEW)]),
    )
    return requests_mock


def test_incremental_read_emits_only_blocks_edited_since_state(notion_api):
    """
    With a prior global cursor, unchanged leaf blocks must not be re-emitted. Blocks with children are still emitted so
    that the retriever keeps recursing into them: an edited nested block under an unchanged parent must not be lost.
    """
    output = _read_blocks({"state": {"last_edited_time": _STATE_CURSOR}, "use_global_cursor": True, "lookback_window": 0})

    assert sorted(record.record.data["id"] for record in output.records) == ["new-leaf", "new-nested", "old-toggle"]
    assert output.most_recent_state.stream_state.state == {"last_edited_time": "2025-06-01T00:00:00.000000Z"}


def test_first_incremental_read_emits_all_blocks_after_start_date(notion_api):
    output = _read_blocks(None)

    assert sorted(record.record.data["id"] for record in output.records) == [
        "new-leaf",
        "new-nested",
        "old-leaf-1",
        "old-leaf-2",
        "old-nested",
        "old-toggle",
    ]
