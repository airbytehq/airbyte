# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from typing import Any, Dict, List, Optional

import pytest

from airbyte_cdk.models import ConfiguredAirbyteCatalogSerializer
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


_CONFIG = {"start_date": "2020-01-01T00:00:00.000Z", "credentials": {"auth_type": "token", "token": "abcd"}}
_PRIOR_CURSOR = "2026-01-01T00:00:00.000Z"
_OLD = "2025-06-01T00:00:00.000Z"
_AT_CURSOR = _PRIOR_CURSOR
_NEW = "2026-01-10T00:00:00.000Z"
_NEWEST = "2026-01-15T00:00:00.000Z"


def _block(block_id: str, last_edited_time: str, parent_id: str, has_children: bool = False) -> Dict[str, Any]:
    return {
        "object": "block",
        "id": block_id,
        "parent": {"type": "page_id", "page_id": parent_id},
        "created_time": _OLD,
        "last_edited_time": last_edited_time,
        "has_children": has_children,
        "archived": False,
        "in_trash": False,
        "type": "paragraph",
        "paragraph": {"rich_text": []},
    }


def _list_response(results: List[Dict[str, Any]]) -> HttpResponse:
    return HttpResponse(json.dumps({"object": "list", "results": results, "has_more": False, "next_cursor": None}), 200)


def _children_request(block_id: str) -> HttpRequest:
    return HttpRequest(url=f"https://api.notion.com/v1/blocks/{block_id}/children", query_params={"page_size": "100"})


def _given_page_with_block_tree(http_mocker: HttpMocker) -> HttpRequest:
    """
    page-1
    ├── old-parent (edited before the prior cursor, has children)
    │   ├── new-child (edited after the prior cursor)
    │   └── old-child
    ├── at-cursor-leaf (edited exactly at the prior cursor)
    ├── new-leaf
    └── old-leaf
    """
    http_mocker.post(
        HttpRequest(
            url="https://api.notion.com/v1/search",
            body={
                "sort": {"direction": "descending", "timestamp": "last_edited_time"},
                "filter": {"property": "object", "value": "page"},
                "page_size": 100,
            },
        ),
        _list_response([{"object": "page", "id": "page-1", "last_edited_time": _NEWEST, "properties": {}}]),
    )
    http_mocker.get(
        _children_request("page-1"),
        _list_response(
            [
                _block("old-parent", _OLD, "page-1", has_children=True),
                _block("at-cursor-leaf", _AT_CURSOR, "page-1"),
                _block("new-leaf", _NEWEST, "page-1"),
                _block("old-leaf", _OLD, "page-1"),
            ]
        ),
    )
    old_parent_children_request = _children_request("old-parent")
    http_mocker.get(
        old_parent_children_request,
        _list_response([_block("new-child", _NEW, "old-parent"), _block("old-child", _OLD, "old-parent")]),
    )
    return old_parent_children_request


def _read_blocks(state: Optional[List[Any]]) -> EntrypointOutput:
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
    source = get_source(_CONFIG, state)
    return read(source, config=_CONFIG, catalog=catalog, state=state)


@pytest.mark.parametrize(
    "prior_state",
    [
        pytest.param({"last_edited_time": _PRIOR_CURSOR}, id="legacy_flat_state"),
        pytest.param(
            {"use_global_cursor": True, "state": {"last_edited_time": _PRIOR_CURSOR}, "lookback_window": 0, "parent_state": {}},
            id="global_cursor_state",
        ),
    ],
)
def test_given_prior_state_when_read_blocks_then_emit_only_blocks_edited_since_cursor(prior_state) -> None:
    """
    Blocks edited before the prior cursor are not emitted again, while the children of an unchanged block are still
    traversed so edited nested blocks are not missed. The cursor comparison is inclusive, so a block edited exactly at
    the cursor is re-emitted.
    """
    with HttpMocker() as http_mocker:
        old_parent_children_request = _given_page_with_block_tree(http_mocker)
        output = _read_blocks(StateBuilder().with_stream_state("blocks", prior_state).build())
        http_mocker.assert_number_of_calls(old_parent_children_request, 1)

    assert sorted(record.record.data["id"] for record in output.records) == ["at-cursor-leaf", "new-child", "new-leaf"]
    assert output.most_recent_state.stream_state.__dict__["state"] == {"last_edited_time": "2026-01-15T00:00:00.000000Z"}


def test_given_no_state_when_read_blocks_then_emit_all_blocks() -> None:
    with HttpMocker() as http_mocker:
        _given_page_with_block_tree(http_mocker)
        output = _read_blocks(None)

    assert sorted(record.record.data["id"] for record in output.records) == [
        "at-cursor-leaf",
        "new-child",
        "new-leaf",
        "old-child",
        "old-leaf",
        "old-parent",
    ]
    assert output.most_recent_state.stream_state.__dict__["state"] == {"last_edited_time": "2026-01-15T00:00:00.000000Z"}
