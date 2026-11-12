#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#
import json
from typing import Any, List, Mapping, Optional

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


_CONFIG = {"start_date": "2020-01-01T00:00:00.000Z", "credentials": {"auth_type": "token", "token": "abcd"}}
_API = "https://api.notion.com/v1"
_PAGE_ID = "page-1"
_SEARCH_PAGES_BODY = {
    "sort": {"direction": "descending", "timestamp": "last_edited_time"},
    "filter": {"property": "object", "value": "page"},
    "page_size": 100,
}


def _block(block_id: str, last_edited_time: str, parent_id: str, has_children: bool = False) -> Mapping[str, Any]:
    return {
        "object": "block",
        "id": block_id,
        "parent": {
            "type": "page_id" if parent_id == _PAGE_ID else "block_id",
            "page_id" if parent_id == _PAGE_ID else "block_id": parent_id,
        },
        "created_time": "2020-06-01T00:00:00.000Z",
        "last_edited_time": last_edited_time,
        "has_children": has_children,
        "archived": False,
        "in_trash": False,
        "type": "paragraph",
        "paragraph": {"rich_text": [], "color": "default"},
    }


def _list(results: List[Mapping[str, Any]]) -> HttpResponse:
    return HttpResponse(json.dumps({"object": "list", "results": results, "next_cursor": None, "has_more": False}), 200)


def _mock_workspace(http_mocker: HttpMocker, page_blocks: List[Mapping[str, Any]], toggle_children: List[Mapping[str, Any]]) -> None:
    http_mocker.post(
        HttpRequest(url=f"{_API}/search", body=json.dumps(_SEARCH_PAGES_BODY)),
        _list([{"object": "page", "id": _PAGE_ID, "last_edited_time": "2025-03-01T00:00:00.000Z", "properties": {}}]),
    )
    http_mocker.get(HttpRequest(url=f"{_API}/blocks/{_PAGE_ID}/children", query_params={"page_size": "100"}), _list(page_blocks))
    http_mocker.get(HttpRequest(url=f"{_API}/blocks/toggle/children", query_params={"page_size": "100"}), _list(toggle_children))


def _read_blocks(state: Optional[List[Any]] = None) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream("blocks", SyncMode.incremental).build()
    return read(get_source(_CONFIG, state), _CONFIG, catalog, state)


def _emitted_ids(output: EntrypointOutput) -> List[str]:
    return sorted(record.record.data["id"] for record in output.records)


def test_incremental_read_emits_only_blocks_edited_since_state_including_nested_children():
    first_sync_cursor = "2024-01-01T00:00:00.000Z"
    with HttpMocker() as http_mocker:
        _mock_workspace(
            http_mocker,
            page_blocks=[
                _block("unchanged", "2023-06-01T00:00:00.000Z", _PAGE_ID),
                _block("toggle", "2023-06-01T00:00:00.000Z", _PAGE_ID, has_children=True),
                _block("latest", first_sync_cursor, _PAGE_ID),
            ],
            toggle_children=[_block("unchanged-child", "2023-06-01T00:00:00.000Z", "toggle")],
        )
        first = _read_blocks()

    assert _emitted_ids(first) == ["latest", "toggle", "unchanged", "unchanged-child"]
    first_state = first.most_recent_state.stream_state.__dict__
    assert first_state["state"] == {"last_edited_time": "2024-01-01T00:00:00.000000Z"}

    with HttpMocker() as http_mocker:
        _mock_workspace(
            http_mocker,
            page_blocks=[
                _block("unchanged", "2023-06-01T00:00:00.000Z", _PAGE_ID),
                # Editing a nested block is not guaranteed to update its parent's last_edited_time, so the
                # parent must still be traversed even though it is not emitted again.
                _block("toggle", "2023-06-01T00:00:00.000Z", _PAGE_ID, has_children=True),
                _block("latest", first_sync_cursor, _PAGE_ID),
                _block("edited", "2025-02-01T00:00:00.000Z", _PAGE_ID),
            ],
            toggle_children=[
                _block("unchanged-child", "2023-06-01T00:00:00.000Z", "toggle"),
                _block("edited-child", "2025-03-01T00:00:00.000Z", "toggle"),
            ],
        )
        second = _read_blocks(StateBuilder().with_stream_state("blocks", first_state).build())

    # "latest" sits exactly on the saved cursor and is re-emitted: the cursor is inclusive (plus the
    # global cursor's lookback window), which is the documented overlap. Nothing older is emitted again.
    assert _emitted_ids(second) == ["edited", "edited-child", "latest"]
    assert second.most_recent_state.stream_state.__dict__["state"] == {"last_edited_time": "2025-03-01T00:00:00.000000Z"}
