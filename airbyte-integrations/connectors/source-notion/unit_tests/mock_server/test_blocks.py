# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from typing import Any, Dict, List, Optional

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


_STREAM_NAME = "blocks"
_URL_BASE = "https://api.notion.com/v1"
_CONFIG = {"start_date": "2020-01-01T00:00:00.000Z", "credentials": {"auth_type": "token", "token": "token"}}

_OCTOBER_1 = "2021-10-01T00:00:00.000Z"
_OCTOBER_2 = "2021-10-02T00:00:00.000Z"
_OCTOBER_3 = "2021-10-03T00:00:00.000Z"
_NOVEMBER_19 = "2021-11-19T13:33:00.000Z"
_DECEMBER_1 = "2021-12-01T00:00:00.000Z"


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


def _list_response(results: List[Dict[str, Any]]) -> HttpResponse:
    return HttpResponse(json.dumps({"object": "list", "results": results, "next_cursor": None, "has_more": False}), 200)


def _mock_workspace(http_mocker: HttpMocker, unchanged_parent_child_edited_at: str) -> None:
    """
    page-1
    ├── unchanged-leaf
    ├── edited-parent
    │   ├── unchanged-child
    │   └── edited-child
    └── unchanged-parent
        └── child-of-unchanged-parent   <- `last_edited_time` varies between the two syncs
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
        _list_response([{"object": "page", "id": "page-1", "last_edited_time": _DECEMBER_1, "properties": {}}]),
    )
    http_mocker.get(
        HttpRequest(url=f"{_URL_BASE}/blocks/page-1/children", query_params={"page_size": "100"}),
        _list_response(
            [
                _block("unchanged-leaf", _OCTOBER_1),
                _block("edited-parent", _NOVEMBER_19, has_children=True),
                _block("unchanged-parent", _OCTOBER_2, has_children=True),
            ]
        ),
    )
    http_mocker.get(
        HttpRequest(url=f"{_URL_BASE}/blocks/edited-parent/children", query_params={"page_size": "100"}),
        _list_response([_block("unchanged-child", _OCTOBER_3), _block("edited-child", _NOVEMBER_19)]),
    )
    http_mocker.get(
        HttpRequest(url=f"{_URL_BASE}/blocks/unchanged-parent/children", query_params={"page_size": "100"}),
        _list_response([_block("child-of-unchanged-parent", unchanged_parent_child_edited_at)]),
    )


def _read(state: Optional[Dict[str, Any]] = None) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
    state_messages = StateBuilder().with_stream_state(_STREAM_NAME, state or {}).build()
    return read(get_source(_CONFIG, state_messages), _CONFIG, catalog, state_messages)


def _record_ids(output: EntrypointOutput) -> List[str]:
    return sorted(record.record.data["id"] for record in output.records)


def test_incremental_read_with_state_emits_only_blocks_edited_since_the_last_sync():
    with HttpMocker() as http_mocker:
        _mock_workspace(http_mocker, unchanged_parent_child_edited_at=_OCTOBER_3)
        first_read = _read()

    assert _record_ids(first_read) == [
        "child-of-unchanged-parent",
        "edited-child",
        "edited-parent",
        "unchanged-child",
        "unchanged-leaf",
        "unchanged-parent",
    ]
    first_state = first_read.most_recent_state.stream_state.__dict__
    assert first_state["state"] == {"last_edited_time": "2021-11-19T13:33:00.000000Z"}

    # Between the two syncs only `child-of-unchanged-parent` is edited; its parent block keeps its old `last_edited_time`.
    # HttpMocker fails the test if a mocked request is not sent, so this also pins that the children of an unchanged
    # block are still requested.
    with HttpMocker() as http_mocker:
        _mock_workspace(http_mocker, unchanged_parent_child_edited_at=_DECEMBER_1)
        second_read = _read(first_state)

    # The cursor comparison is inclusive, so the two blocks edited exactly at the previous cursor value are emitted
    # again. Nothing older than the cursor is.
    assert _record_ids(second_read) == ["child-of-unchanged-parent", "edited-child", "edited-parent"]
    assert second_read.most_recent_state.stream_state.__dict__["state"] == {"last_edited_time": "2021-12-01T00:00:00.000000Z"}
