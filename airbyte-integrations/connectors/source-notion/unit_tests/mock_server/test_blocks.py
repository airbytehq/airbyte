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
_CONFIG = {"start_date": "2020-01-01T00:00:00.000Z", "credentials": {"auth_type": "token", "token": "abcd"}}
_URL_BASE = "https://api.notion.com/v1"
_PAGE_ID = "page-1"
_PARENT_BLOCK_ID = "unedited-parent"


def _list_response(results: List[Dict[str, Any]]) -> HttpResponse:
    return HttpResponse(json.dumps({"object": "list", "results": results, "next_cursor": None, "has_more": False}), 200)


def _block(block_id: str, last_edited_time: str, parent_id: str = _PAGE_ID, has_children: bool = False) -> Dict[str, Any]:
    return {
        "object": "block",
        "id": block_id,
        "parent": {"type": "page_id", "page_id": parent_id},
        "last_edited_time": last_edited_time,
        "has_children": has_children,
        "type": "paragraph",
    }


def _pages_request() -> HttpRequest:
    return HttpRequest(
        url=f"{_URL_BASE}/search",
        body=json.dumps(
            {
                "sort": {"direction": "descending", "timestamp": "last_edited_time"},
                "filter": {"property": "object", "value": "page"},
                "page_size": 100,
            }
        ),
    )


def _children_request(block_id: str) -> HttpRequest:
    return HttpRequest(url=f"{_URL_BASE}/blocks/{block_id}/children", query_params={"page_size": "100"})


def _given_a_page_with_a_nested_block_tree(http_mocker: HttpMocker) -> HttpRequest:
    """
    Mocks the tree below and returns the request for the children of `unedited-parent`.

    page-1
    ├── unedited-block      2024-01-01
    ├── unedited-parent     2024-01-02
    │   ├── unedited-child  2024-01-03
    │   └── edited-child    2024-03-02
    └── edited-block        2024-03-01
    """
    http_mocker.post(
        _pages_request(),
        _list_response([{"object": "page", "id": _PAGE_ID, "last_edited_time": "2024-03-02T00:00:00.000Z"}]),
    )
    http_mocker.get(
        _children_request(_PAGE_ID),
        _list_response(
            [
                _block("unedited-block", "2024-01-01T00:00:00.000Z"),
                _block(_PARENT_BLOCK_ID, "2024-01-02T00:00:00.000Z", has_children=True),
                _block("edited-block", "2024-03-01T00:00:00.000Z"),
            ]
        ),
    )
    nested_children_request = _children_request(_PARENT_BLOCK_ID)
    http_mocker.get(
        nested_children_request,
        _list_response(
            [
                _block("unedited-child", "2024-01-03T00:00:00.000Z", parent_id=_PARENT_BLOCK_ID),
                _block("edited-child", "2024-03-02T00:00:00.000Z", parent_id=_PARENT_BLOCK_ID),
            ]
        ),
    )
    return nested_children_request


def _read(state: Optional[Dict[str, Any]] = None) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
    state_messages = StateBuilder().with_stream_state(_STREAM_NAME, state).build() if state else StateBuilder().build()
    return read(get_source(_CONFIG, state_messages), _CONFIG, catalog, state_messages)


def _record_ids(output: EntrypointOutput) -> List[str]:
    return [record.record.data["id"] for record in output.records]


def _state(output: EntrypointOutput) -> Dict[str, Any]:
    return output.most_recent_state.stream_state.__dict__


def test_second_incremental_read_only_emits_blocks_at_or_after_the_saved_cursor() -> None:
    with HttpMocker() as http_mocker:
        _given_a_page_with_a_nested_block_tree(http_mocker)
        first_read = _read()

    # children are emitted before the block that holds them
    assert _record_ids(first_read) == ["unedited-block", "unedited-child", "edited-child", _PARENT_BLOCK_ID, "edited-block"]
    assert _state(first_read)["state"] == {"last_edited_time": "2024-03-02T00:00:00.000000Z"}

    with HttpMocker() as http_mocker:
        _given_a_page_with_a_nested_block_tree(http_mocker)
        second_read = _read(_state(first_read))

    # The cursor comparison is inclusive, so the block sitting exactly on the saved cursor is read again. Nothing older is.
    assert _record_ids(second_read) == ["edited-child"]
    assert _state(second_read)["state"] == {"last_edited_time": "2024-03-02T00:00:00.000000Z"}


def test_incremental_read_emits_edited_children_of_a_block_that_was_not_edited() -> None:
    with HttpMocker() as http_mocker:
        nested_children_request = _given_a_page_with_a_nested_block_tree(http_mocker)
        output = _read({"use_global_cursor": True, "state": {"last_edited_time": "2024-02-01T00:00:00.000000Z"}})
        # the unedited parent is not emitted, but its children are still requested
        http_mocker.assert_number_of_calls(nested_children_request, 1)

    assert _record_ids(output) == ["edited-child", "edited-block"]
    assert _state(output)["state"] == {"last_edited_time": "2024-03-02T00:00:00.000000Z"}
