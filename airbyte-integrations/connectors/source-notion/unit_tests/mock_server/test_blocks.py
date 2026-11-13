# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from typing import Any, Dict, List

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


_STREAM_NAME = "blocks"
_URL_BASE = "https://api.notion.com/v1"
_CONFIG = {"start_date": "2020-01-01T00:00:00.000Z", "credentials": {"auth_type": "token", "token": "token"}}
_BEFORE_STATE = "2024-01-01T00:00:00.000Z"
_STATE = "2024-03-01T00:00:00.000Z"
_AFTER_STATE = "2024-06-01T00:00:00.000Z"


def _list_response(results: List[Dict[str, Any]]) -> HttpResponse:
    return HttpResponse(json.dumps({"object": "list", "results": results, "next_cursor": None, "has_more": False}), 200)


def _page(page_id: str, last_edited_time: str) -> Dict[str, Any]:
    return {"object": "page", "id": page_id, "last_edited_time": last_edited_time, "properties": {}}


def _block(block_id: str, parent_id: str, last_edited_time: str, has_children: bool = False) -> Dict[str, Any]:
    return {
        "object": "block",
        "id": block_id,
        "parent": {"type": "page_id", "page_id": parent_id},
        "created_time": "2021-01-01T00:00:00.000Z",
        "last_edited_time": last_edited_time,
        "has_children": has_children,
        "type": "paragraph",
        "paragraph": {"rich_text": [], "color": "default"},
    }


def _pages_search_request() -> HttpRequest:
    return HttpRequest(
        f"{_URL_BASE}/search",
        body={
            "sort": {"direction": "descending", "timestamp": "last_edited_time"},
            "filter": {"property": "object", "value": "page"},
            "page_size": 100,
        },
    )


def _children_request(block_id: str) -> HttpRequest:
    return HttpRequest(f"{_URL_BASE}/blocks/{block_id}/children", query_params={"page_size": "100"})


def test_incremental_read_with_prior_state_emits_only_blocks_edited_since_state() -> None:
    # State shape emitted by the connector itself after a first sync
    state = (
        StateBuilder()
        .with_stream_state(
            _STREAM_NAME,
            {"use_global_cursor": True, "state": {"last_edited_time": _STATE}, "lookback_window": 1, "parent_state": {}},
        )
        .build()
    )
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()

    with HttpMocker() as http_mocker:
        http_mocker.post(_pages_search_request(), _list_response([_page("page-1", _AFTER_STATE)]))
        http_mocker.get(
            _children_request("page-1"),
            _list_response(
                [
                    _block("unchanged-block", "page-1", _BEFORE_STATE),
                    # No children request is mocked for this block: an unchanged block's subtree must not be fetched
                    _block("unchanged-parent", "page-1", _BEFORE_STATE, has_children=True),
                    _block("edited-parent", "page-1", _AFTER_STATE, has_children=True),
                ]
            ),
        )
        http_mocker.get(
            _children_request("edited-parent"),
            _list_response(
                [
                    _block("unchanged-child", "edited-parent", _BEFORE_STATE),
                    _block("edited-child", "edited-parent", _AFTER_STATE),
                ]
            ),
        )

        output = read(get_source(_CONFIG, state), config=_CONFIG, catalog=catalog, state=state)

    assert [record.record.data["id"] for record in output.records] == ["edited-child", "edited-parent"]
    assert output.errors == []
    assert output.most_recent_state.stream_state.state == {"last_edited_time": "2024-06-01T00:00:00.000000Z"}
