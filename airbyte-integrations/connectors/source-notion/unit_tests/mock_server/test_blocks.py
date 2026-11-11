#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#
import json
from typing import Any, Dict, List, Optional

from airbyte_cdk.models import AirbyteStateMessage, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder, ConfiguredAirbyteStreamBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


_CONFIG = {"credentials": {"auth_type": "token", "token": "test-token"}, "start_date": "2020-01-01T00:00:00.000Z"}
_PAGE_ID = "page-1"


def _search_pages_request() -> HttpRequest:
    return HttpRequest(
        url="https://api.notion.com/v1/search",
        body={
            "sort": {"direction": "descending", "timestamp": "last_edited_time"},
            "filter": {"property": "object", "value": "page"},
            "page_size": 100,
        },
    )


def _block_children_request(block_id: str) -> HttpRequest:
    return HttpRequest(url=f"https://api.notion.com/v1/blocks/{block_id}/children", query_params={"page_size": "100"})


def _list_response(results: List[Dict[str, Any]]) -> HttpResponse:
    return HttpResponse(json.dumps({"object": "list", "results": results, "next_cursor": None, "has_more": False}), 200)


def _block(block_id: str, last_edited_time: str, parent_id: str, has_children: bool = False) -> Dict[str, Any]:
    return {
        "object": "block",
        "id": block_id,
        "type": "paragraph",
        "paragraph": {"rich_text": []},
        "parent": {"type": "page_id", "page_id": parent_id},
        "created_time": "2023-12-01T00:00:00.000Z",
        "last_edited_time": last_edited_time,
        "has_children": has_children,
        "archived": False,
        "in_trash": False,
    }


def _given_page_with_blocks(http_mocker: HttpMocker, toggle_child_edited_at: str) -> None:
    """page-1 holds a toggle (with one child) and a paragraph; only the toggle's child edit time varies."""
    page = {"object": "page", "id": _PAGE_ID, "last_edited_time": toggle_child_edited_at, "properties": {}}
    http_mocker.post(_search_pages_request(), _list_response([page]))
    http_mocker.get(
        _block_children_request(_PAGE_ID),
        _list_response(
            [
                _block("toggle", "2024-01-10T00:00:00.000Z", _PAGE_ID, has_children=True),
                _block("paragraph", "2024-02-01T00:00:00.000Z", _PAGE_ID),
            ]
        ),
    )
    http_mocker.get(_block_children_request("toggle"), _list_response([_block("toggle-child", toggle_child_edited_at, "toggle")]))


def _read_blocks(state: Optional[List[AirbyteStateMessage]] = None) -> EntrypointOutput:
    catalog = (
        CatalogBuilder().with_stream(ConfiguredAirbyteStreamBuilder().with_name("blocks").with_sync_mode(SyncMode.incremental)).build()
    )
    return read(get_source(_CONFIG, state), _CONFIG, catalog, state)


def test_second_incremental_read_emits_only_blocks_edited_since_the_first_read():
    with HttpMocker() as http_mocker:
        _given_page_with_blocks(http_mocker, toggle_child_edited_at="2024-01-05T00:00:00.000Z")
        first_read = _read_blocks()

    assert [record.record.data["id"] for record in first_read.records] == ["toggle-child", "toggle", "paragraph"]
    first_state = first_read.most_recent_state.stream_state.__dict__
    assert first_state["state"] == {"last_edited_time": "2024-02-01T00:00:00.000000Z"}

    # Only the nested child is edited after the first read; its parent toggle keeps its old edit time,
    # so the toggle's children must still be requested (HttpMocker fails on any unused mock).
    with HttpMocker() as http_mocker:
        _given_page_with_blocks(http_mocker, toggle_child_edited_at="2024-03-01T00:00:00.000Z")
        second_read = _read_blocks(state=StateBuilder().with_stream_state("blocks", first_state).build())

    # `paragraph` sits exactly on the stored cursor value, which is inclusive, so it is the expected overlap.
    assert [record.record.data["id"] for record in second_read.records] == ["toggle-child", "paragraph"]
    assert second_read.most_recent_state.stream_state.__dict__["state"] == {"last_edited_time": "2024-03-01T00:00:00.000000Z"}
