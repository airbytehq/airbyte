# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase
from typing import Any, Dict, List, Optional

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source
from unit_tests.mock_server.config import ConfigBuilder


_STREAM_NAME = "blocks"
_URL_BASE = "https://api.notion.com/v1"
_STATE_CURSOR_VALUE = "2024-01-01T00:00:00.000Z"
_OLD = "2023-06-01T00:00:00.000Z"
_NEW = "2024-06-01T00:00:00.000Z"


def _list_response(results: List[Dict[str, Any]]) -> HttpResponse:
    return HttpResponse(json.dumps({"object": "list", "results": results, "next_cursor": None, "has_more": False}), 200)


def _page(page_id: str, last_edited_time: str) -> Dict[str, Any]:
    return {"object": "page", "id": page_id, "last_edited_time": last_edited_time, "properties": {}}


def _block(block_id: str, last_edited_time: str, has_children: bool = False) -> Dict[str, Any]:
    return {
        "object": "block",
        "id": block_id,
        "parent": {"type": "page_id", "page_id": "page-1"},
        "created_time": "2021-01-01T00:00:00.000Z",
        "last_edited_time": last_edited_time,
        "has_children": has_children,
        "type": "paragraph",
        "paragraph": {"rich_text": []},
    }


def _pages_search_request() -> HttpRequest:
    return HttpRequest(
        url=f"{_URL_BASE}/search",
        body={
            "sort": {"direction": "descending", "timestamp": "last_edited_time"},
            "filter": {"property": "object", "value": "page"},
            "page_size": 100,
        },
    )


def _children_request(block_id: str) -> HttpRequest:
    return HttpRequest(url=f"{_URL_BASE}/blocks/{block_id}/children", query_params={"page_size": "100"})


def _mock_block_tree(http_mocker: HttpMocker) -> None:
    """
    page-1
      ├── old-block            (not edited since state)
      ├── old-parent           (not edited since state, has children)
      │     ├── old-nested     (not edited since state)
      │     └── new-nested     (edited after state)
      └── new-block            (edited after state)
    """
    http_mocker.post(_pages_search_request(), _list_response([_page("page-1", _NEW)]))
    http_mocker.get(
        _children_request("page-1"),
        _list_response([_block("old-block", _OLD), _block("old-parent", _OLD, has_children=True), _block("new-block", _NEW)]),
    )
    http_mocker.get(_children_request("old-parent"), _list_response([_block("old-nested", _OLD), _block("new-nested", _NEW)]))


def _read(state: Optional[List[Any]]) -> EntrypointOutput:
    config = ConfigBuilder().build()
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
    return read(get_source(config, state), config=config, catalog=catalog, state=state)


class BlocksIncrementalTest(TestCase):
    @HttpMocker()
    def test_incremental_read_with_state_emits_only_blocks_edited_since_state(self, http_mocker: HttpMocker) -> None:
        _mock_block_tree(http_mocker)
        state = (
            StateBuilder()
            .with_stream_state(
                _STREAM_NAME,
                {"use_global_cursor": True, "state": {"last_edited_time": _STATE_CURSOR_VALUE}, "lookback_window": 1, "parent_state": {}},
            )
            .build()
        )

        output = _read(state)

        assert sorted(record.record.data["id"] for record in output.records) == ["new-block", "new-nested"]
        assert output.most_recent_state.stream_state.state == {"last_edited_time": "2024-06-01T00:00:00.000000Z"}

    @HttpMocker()
    def test_incremental_read_without_state_emits_all_blocks(self, http_mocker: HttpMocker) -> None:
        _mock_block_tree(http_mocker)

        output = _read(None)

        assert sorted(record.record.data["id"] for record in output.records) == [
            "new-block",
            "new-nested",
            "old-block",
            "old-nested",
            "old-parent",
        ]
        assert output.most_recent_state.stream_state.state == {"last_edited_time": "2024-06-01T00:00:00.000000Z"}
