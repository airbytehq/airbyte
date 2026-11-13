# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from typing import Any, Dict, List, Optional

import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


_STREAM_NAME = "blocks"
_URL_BASE = "https://api.notion.com/v1"
_CONFIG = {"start_date": "2020-01-01T00:00:00.000Z", "credentials": {"auth_type": "token", "token": "abcd"}}

_BEFORE_STATE = "2021-06-01T00:00:00.000Z"
_STATE_CURSOR = "2022-01-01T00:00:00.000Z"
_AFTER_STATE = "2022-06-01T00:00:00.000Z"
_LATEST = "2022-07-01T00:00:00.000Z"


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
        "paragraph": {"rich_text": [], "color": "default"},
    }


def _list_response(results: List[Dict[str, Any]], next_cursor: Optional[str] = None) -> HttpResponse:
    return HttpResponse(json.dumps({"object": "list", "results": results, "next_cursor": next_cursor, "has_more": bool(next_cursor)}), 200)


def _children_request(block_id: str, start_cursor: Optional[str] = None) -> HttpRequest:
    query_params = {"page_size": "100"}
    if start_cursor:
        query_params["start_cursor"] = start_cursor
    return HttpRequest(url=f"{_URL_BASE}/blocks/{block_id}/children", query_params=query_params)


def _given_block_tree(http_mocker: HttpMocker) -> None:
    """
    page-1
    ├── old-leaf            (edited before state)
    ├── new-parent          (edited after state)
    │   ├── old-child       (edited before state)
    │   └── new-child       (edited after state)
    ├── old-parent          (edited before state, second page of page-1's children)
    │   └── newest-child    (edited after state: only reachable through a block that is itself filtered out)
    └── at-state-leaf       (edited exactly at the state cursor)
    """
    http_mocker.post(
        HttpRequest(
            url=f"{_URL_BASE}/search",
            body={
                "sort": {"direction": "descending", "timestamp": "last_edited_time"},
                "filter": {"property": "object", "value": "page"},
                "page_size": 100,
            },
        ),
        _list_response([{"object": "page", "id": "page-1", "last_edited_time": _LATEST}]),
    )
    http_mocker.get(
        _children_request("page-1"),
        _list_response([_block("old-leaf", _BEFORE_STATE), _block("new-parent", _AFTER_STATE, has_children=True)], next_cursor="cursor-2"),
    )
    http_mocker.get(
        _children_request("page-1", start_cursor="cursor-2"),
        _list_response([_block("old-parent", _BEFORE_STATE, has_children=True), _block("at-state-leaf", _STATE_CURSOR)]),
    )
    http_mocker.get(
        _children_request("new-parent"),
        _list_response([_block("old-child", _BEFORE_STATE), _block("new-child", _AFTER_STATE)]),
    )
    http_mocker.get(_children_request("old-parent"), _list_response([_block("newest-child", _LATEST)]))


def _read(config: Dict[str, Any], state: Optional[List[Any]] = None) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
    return read(get_source(config, state), config=config, catalog=catalog, state=state)


def test_given_no_state_when_read_then_emit_every_block_and_latest_cursor() -> None:
    # A first sync emits every block of the pages it reads, including blocks last edited before `start_date`.
    config = {**_CONFIG, "start_date": _STATE_CURSOR}

    with HttpMocker() as http_mocker:
        _given_block_tree(http_mocker)
        output = _read(config)

    assert sorted(record.record.data["id"] for record in output.records) == [
        "at-state-leaf",
        "new-child",
        "new-parent",
        "newest-child",
        "old-child",
        "old-leaf",
        "old-parent",
    ]
    assert output.most_recent_state.stream_state.__dict__["state"] == {"last_edited_time": "2022-07-01T00:00:00.000000Z"}


@pytest.mark.parametrize(
    "stream_state",
    [
        pytest.param(
            {"state": {"last_edited_time": _STATE_CURSOR}, "use_global_cursor": True, "lookback_window": 0}, id="global_cursor_state"
        ),
        pytest.param({"last_edited_time": _STATE_CURSOR}, id="legacy_flat_state"),
    ],
)
def test_given_state_when_read_then_emit_only_blocks_edited_since_state(stream_state: Dict[str, Any]) -> None:
    state = StateBuilder().with_stream_state(_STREAM_NAME, stream_state).build()

    with HttpMocker() as http_mocker:
        _given_block_tree(http_mocker)
        output = _read(_CONFIG, state)

    # Blocks edited before the state cursor are dropped, but their children are still traversed:
    # `newest-child` sits under `old-parent`, whose own `last_edited_time` did not move.
    assert sorted(record.record.data["id"] for record in output.records) == ["at-state-leaf", "new-child", "new-parent", "newest-child"]
    assert output.most_recent_state.stream_state.__dict__["state"] == {"last_edited_time": "2022-07-01T00:00:00.000000Z"}
