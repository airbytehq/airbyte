# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from typing import Any, Dict, List

from airbyte_cdk.models import AirbyteStateMessage, ConfiguredAirbyteCatalogSerializer
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse

from unit_tests.conftest import get_source


_CONFIG = {"start_date": "2021-01-01T00:00:00.000Z", "credentials": {"auth_type": "token", "token": "test-token"}}
_API = "https://api.notion.com/v1"
_PAGE_ID = "page-1"


def _list_response(results: List[Dict[str, Any]]) -> HttpResponse:
    return HttpResponse(json.dumps({"object": "list", "results": results, "next_cursor": None, "has_more": False}), 200)


def _block(block_id: str, last_edited_time: str, has_children: bool = False) -> Dict[str, Any]:
    return {
        "object": "block",
        "id": block_id,
        "parent": {"type": "page_id", "page_id": _PAGE_ID},
        "created_time": "2021-02-01T00:00:00.000Z",
        "last_edited_time": last_edited_time,
        "has_children": has_children,
        "archived": False,
        "in_trash": False,
        "type": "paragraph",
        "paragraph": {"rich_text": [], "color": "default"},
    }


def _given_api(http_mocker: HttpMocker, page_blocks: List[Dict[str, Any]], children_by_block: Dict[str, List[Dict[str, Any]]]) -> None:
    http_mocker.post(
        HttpRequest(
            url=f"{_API}/search",
            body={
                "sort": {"direction": "descending", "timestamp": "last_edited_time"},
                "filter": {"property": "object", "value": "page"},
                "page_size": 100,
            },
        ),
        _list_response([{"object": "page", "id": _PAGE_ID, "last_edited_time": "2021-12-01T00:00:00.000Z", "properties": {}}]),
    )
    http_mocker.get(HttpRequest(url=f"{_API}/blocks/{_PAGE_ID}/children", query_params={"page_size": "100"}), _list_response(page_blocks))
    for block_id, children in children_by_block.items():
        http_mocker.get(HttpRequest(url=f"{_API}/blocks/{block_id}/children", query_params={"page_size": "100"}), _list_response(children))


def _read_blocks(state: List[AirbyteStateMessage]) -> EntrypointOutput:
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
    return read(get_source(_CONFIG, state), config=_CONFIG, catalog=catalog, state=state)


def _record_ids(output: EntrypointOutput) -> List[str]:
    return sorted(record.record.data["id"] for record in output.records)


def _cursor(output: EntrypointOutput) -> str:
    return output.most_recent_state.stream_state.__dict__["state"]["last_edited_time"]


def test_incremental_read_emits_only_blocks_edited_since_previous_sync():
    """
    Second sync, run with the state the first one emitted, must only emit blocks edited since that state,
    including a nested child block that was edited while its parent block was not. `blocks` is client-side
    incremental with an inclusive lower bound, so a block edited exactly at the stored cursor is re-emitted.
    """
    with HttpMocker() as http_mocker:
        _given_api(
            http_mocker,
            page_blocks=[_block("block-1", "2021-10-01T00:00:00.000Z"), _block("block-2", "2021-11-01T00:00:00.000Z", has_children=True)],
            children_by_block={"block-2": [_block("block-2-child", "2021-11-15T00:00:00.000Z")]},
        )
        first_sync = _read_blocks(state=[])

    assert _record_ids(first_sync) == ["block-1", "block-2", "block-2-child"]
    assert _cursor(first_sync) == "2021-11-15T00:00:00.000000Z"

    with HttpMocker() as http_mocker:
        _given_api(
            http_mocker,
            page_blocks=[
                _block("block-1", "2021-10-01T00:00:00.000Z"),
                _block("block-2", "2021-11-01T00:00:00.000Z", has_children=True),
                _block("block-3", "2021-11-15T00:00:00.000Z"),
            ],
            children_by_block={"block-2": [_block("block-2-child", "2021-12-01T00:00:00.000Z")]},
        )
        second_sync = _read_blocks(state=[first_sync.state_messages[-1].state])

    # block-1 and block-2 were not edited since the first sync; block-3 sits exactly on the stored cursor
    assert _record_ids(second_sync) == ["block-2-child", "block-3"]
    assert _cursor(second_sync) == "2021-12-01T00:00:00.000000Z"
