# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from typing import Any, Dict, List, Optional

import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


# start_date sits between the old and the new blocks so the tests can tell state filtering from start_date filtering
_CONFIG = {"start_date": "2022-06-01T00:00:00.000Z", "credentials": {"auth_type": "token", "token": "test-token"}}
_API = "https://api.notion.com/v1"
_STREAM = "blocks"

_OLD = "2022-01-01T00:00:00.000Z"
_STATE_CURSOR = "2023-01-01T00:00:00.000Z"
_NEW = "2023-06-01T00:00:00.000Z"


def _page(page_id: str, last_edited_time: str) -> Dict[str, Any]:
    return {
        "object": "page",
        "id": page_id,
        "created_time": "2020-06-01T00:00:00.000Z",
        "last_edited_time": last_edited_time,
        "parent": {"type": "workspace", "workspace": True},
        "archived": False,
        "in_trash": False,
        "properties": {},
    }


def _block(block_id: str, last_edited_time: str, parent_page_id: str = "page-1", has_children: bool = False) -> Dict[str, Any]:
    return {
        "object": "block",
        "id": block_id,
        "parent": {"type": "page_id", "page_id": parent_page_id},
        "created_time": "2020-06-01T00:00:00.000Z",
        "last_edited_time": last_edited_time,
        "has_children": has_children,
        "archived": False,
        "in_trash": False,
        "type": "paragraph",
        "paragraph": {"rich_text": [], "color": "default"},
    }


def _list_response(results: List[Dict[str, Any]]) -> HttpResponse:
    return HttpResponse(json.dumps({"object": "list", "results": results, "next_cursor": None, "has_more": False}), 200)


def _search_pages_request() -> HttpRequest:
    return HttpRequest(
        url=f"{_API}/search",
        body=json.dumps(
            {
                "sort": {"direction": "descending", "timestamp": "last_edited_time"},
                "filter": {"property": "object", "value": "page"},
                "page_size": 100,
            }
        ),
    )


def _children_request(block_id: str) -> HttpRequest:
    return HttpRequest(url=f"{_API}/blocks/{block_id}/children", query_params={"page_size": "100"})


def _read(sync_mode: SyncMode, state: Optional[Dict[str, Any]]):
    catalog = CatalogBuilder().with_stream(_STREAM, sync_mode).build()
    state_messages = StateBuilder().with_stream_state(_STREAM, state).build() if state is not None else None
    source = get_source(_CONFIG, state_messages)
    return read(source, config=_CONFIG, catalog=catalog, state=state_messages)


@pytest.mark.parametrize(
    "sync_mode, state, expected_ids",
    [
        pytest.param(
            SyncMode.full_refresh,
            None,
            {"old-parent", "old-child", "new-child", "new-top", "at-cursor"},
            id="full_refresh_emits_every_block",
        ),
        pytest.param(
            SyncMode.incremental,
            None,
            {"old-parent", "old-child", "new-child", "new-top", "at-cursor"},
            id="first_incremental_sync_emits_every_block",
        ),
        pytest.param(
            SyncMode.incremental,
            {"use_global_cursor": True, "state": {"last_edited_time": _STATE_CURSOR}, "lookback_window": 0},
            {"new-child", "new-top", "at-cursor"},
            id="incremental_sync_emits_only_blocks_edited_at_or_after_state",
        ),
    ],
)
def test_blocks_read_filters_on_state_and_still_walks_children(sync_mode, state, expected_ids):
    """
    With a saved state, the blocks stream must only emit blocks whose `last_edited_time` is at or after the state
    cursor (the cursor value itself is inclusive), while still walking the children of unchanged parent blocks:
    a parent block's `last_edited_time` is not guaranteed to change when only one of its children changes, so
    skipping the traversal would silently drop edited child blocks.
    Without a saved state every block is emitted, including blocks last edited before `start_date`.
    """
    with HttpMocker() as http_mocker:
        http_mocker.post(_search_pages_request(), _list_response([_page("page-1", _NEW)]))
        http_mocker.get(
            _children_request("page-1"),
            _list_response(
                [
                    _block("old-parent", _OLD, has_children=True),
                    _block("new-top", _NEW),
                    _block("at-cursor", _STATE_CURSOR),
                ]
            ),
        )
        http_mocker.get(
            _children_request("old-parent"),
            _list_response([_block("old-child", _OLD), _block("new-child", _NEW)]),
        )

        output = _read(sync_mode, state)

    emitted_ids = [record.record.data["id"] for record in output.records]
    assert sorted(emitted_ids) == sorted(expected_ids)
    assert len(emitted_ids) == len(set(emitted_ids))
    if sync_mode == SyncMode.incremental:
        assert output.most_recent_state.stream_state.state == {"last_edited_time": "2023-06-01T00:00:00.000000Z"}
