#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#
import json
from typing import Any, Dict, List, Optional

from airbyte_cdk.models import AirbyteStateMessage, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


_CONFIG = {"start_date": "2020-01-01T00:00:00.000Z", "credentials": {"auth_type": "token", "token": "abcd"}}
_BASE_URL = "https://api.notion.com/v1"
_OLD = "2023-01-01T00:00:00.000Z"
_NEW = "2023-07-01T00:00:00.000Z"


def _block(block_id: str, last_edited_time: str, has_children: bool = False) -> Dict[str, Any]:
    return {
        "object": "block",
        "id": block_id,
        "parent": {"type": "page_id", "page_id": "page-1"},
        "created_time": _OLD,
        "last_edited_time": last_edited_time,
        "has_children": has_children,
        "archived": False,
        "in_trash": False,
        "type": "paragraph",
        "paragraph": {"rich_text": []},
    }


def _list_response(results: List[Dict[str, Any]]) -> HttpResponse:
    return HttpResponse(json.dumps({"object": "list", "results": results, "next_cursor": None, "has_more": False}), 200)


def _mock_page_with_nested_blocks(http_mocker: HttpMocker) -> None:
    http_mocker.post(
        HttpRequest(
            url=f"{_BASE_URL}/search",
            body={
                "sort": {"direction": "descending", "timestamp": "last_edited_time"},
                "filter": {"property": "object", "value": "page"},
                "page_size": 100,
            },
        ),
        _list_response([{"object": "page", "id": "page-1", "last_edited_time": _NEW, "properties": {}}]),
    )
    http_mocker.get(
        HttpRequest(url=f"{_BASE_URL}/blocks/page-1/children", query_params={"page_size": "100"}),
        _list_response([_block("old-block", _OLD), _block("new-block", _NEW, has_children=True)]),
    )
    http_mocker.get(
        HttpRequest(url=f"{_BASE_URL}/blocks/new-block/children", query_params={"page_size": "100"}),
        _list_response([_block("old-child", _OLD), _block("new-child", "2023-08-01T00:00:00.000Z")]),
    )


def _read_blocks(state: Optional[List[AirbyteStateMessage]]) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream("blocks", SyncMode.incremental).build()
    state = state or StateBuilder().build()
    return read(get_source(_CONFIG, state), config=_CONFIG, catalog=catalog, state=state)


def _record_ids(output: EntrypointOutput) -> List[str]:
    return [record.record.data["id"] for record in output.records]


def test_blocks_incremental_read_skips_blocks_not_edited_since_state():
    with HttpMocker() as http_mocker:
        _mock_page_with_nested_blocks(http_mocker)
        first = _read_blocks(state=None)

    assert _record_ids(first) == ["old-block", "old-child", "new-child", "new-block"]
    first_state = first.most_recent_state.stream_state.__dict__
    assert first_state["state"] == {"last_edited_time": "2023-08-01T00:00:00.000000Z"}

    second_state = StateBuilder().with_stream_state("blocks", {**first_state, "state": {"last_edited_time": _NEW}}).build()
    with HttpMocker() as http_mocker:
        _mock_page_with_nested_blocks(http_mocker)
        second = _read_blocks(state=second_state)

    # Blocks last edited before the state are dropped at every nesting level. The block edited exactly at the
    # state value is emitted again: the cursor is inclusive and the stream uses a one-second lookback window.
    assert _record_ids(second) == ["new-child", "new-block"]
    assert second.most_recent_state.stream_state.__dict__["state"] == {"last_edited_time": "2023-08-01T00:00:00.000000Z"}
