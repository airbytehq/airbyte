# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from typing import Any, Dict, List, Optional

import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder, ConfiguredAirbyteStreamBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


_API_URL = "https://api.notion.com/v1"
_CONFIG = {"credentials": {"auth_type": "token", "token": "test-token"}, "start_date": "2020-01-01T00:00:00.000Z"}
_SEARCH_PAGES_BODY = {
    "sort": {"direction": "descending", "timestamp": "last_edited_time"},
    "filter": {"property": "object", "value": "page"},
    "page_size": 100,
}


def _list_response(results: List[Dict[str, Any]]) -> HttpResponse:
    return HttpResponse(body=_json({"object": "list", "results": results, "next_cursor": None, "has_more": False}), status_code=200)


def _json(body: Dict[str, Any]) -> str:
    return json.dumps(body)


def _page(page_id: str, last_edited_time: str) -> Dict[str, Any]:
    return {
        "object": "page",
        "id": page_id,
        "last_edited_time": last_edited_time,
        "parent": {"type": "workspace", "workspace": True},
        "properties": {},
    }


def _block(block_id: str, parent_id: str, last_edited_time: str, has_children: bool = False) -> Dict[str, Any]:
    return {
        "object": "block",
        "id": block_id,
        "type": "paragraph",
        "has_children": has_children,
        "last_edited_time": last_edited_time,
        "parent": {"type": "page_id", "page_id": parent_id},
    }


def _block_children_request(block_id: str) -> HttpRequest:
    return HttpRequest(url=f"{_API_URL}/blocks/{block_id}/children", query_params={"page_size": "100"})


def _given_block_tree(http_mocker: HttpMocker) -> None:
    """
    page-1 (edited 2024-09-01)
    ├── old-parent (edited 2023-01-01)
    │   └── new-child-of-old-parent (edited 2024-07-01)
    └── new-parent (edited 2024-06-01)
        ├── old-child (edited 2023-02-01)
        └── new-child (edited 2024-08-01)
    """
    http_mocker.post(
        HttpRequest(url=f"{_API_URL}/search", body=_json(_SEARCH_PAGES_BODY)),
        _list_response([_page("page-1", "2024-09-01T00:00:00.000Z")]),
    )
    http_mocker.get(
        _block_children_request("page-1"),
        _list_response(
            [
                _block("old-parent", "page-1", "2023-01-01T00:00:00.000Z", has_children=True),
                _block("new-parent", "page-1", "2024-06-01T00:00:00.000Z", has_children=True),
            ]
        ),
    )
    http_mocker.get(
        _block_children_request("old-parent"),
        _list_response([_block("new-child-of-old-parent", "old-parent", "2024-07-01T00:00:00.000Z")]),
    )
    http_mocker.get(
        _block_children_request("new-parent"),
        _list_response(
            [
                _block("old-child", "new-parent", "2023-02-01T00:00:00.000Z"),
                _block("new-child", "new-parent", "2024-08-01T00:00:00.000Z"),
            ]
        ),
    )


@pytest.mark.parametrize(
    "prior_state, expected_block_ids",
    [
        pytest.param(
            None,
            {"old-parent", "new-child-of-old-parent", "new-parent", "old-child", "new-child"},
            id="first_sync_emits_every_block",
        ),
        pytest.param(
            {"state": {"last_edited_time": "2024-03-01T00:00:00.000Z"}, "use_global_cursor": True, "lookback_window": 0},
            {"new-child-of-old-parent", "new-parent", "new-child"},
            id="sync_with_state_emits_only_blocks_edited_since_state",
        ),
    ],
)
def test_blocks_incremental_read_filters_on_last_edited_time(prior_state: Optional[Dict[str, Any]], expected_block_ids: set) -> None:
    state = StateBuilder().with_stream_state("blocks", prior_state).build() if prior_state else None
    catalog = (
        CatalogBuilder().with_stream(ConfiguredAirbyteStreamBuilder().with_name("blocks").with_sync_mode(SyncMode.incremental)).build()
    )

    with HttpMocker() as http_mocker:
        _given_block_tree(http_mocker)
        output = read(get_source(_CONFIG, state), config=_CONFIG, catalog=catalog, state=state)

    assert sorted(record.record.data["id"] for record in output.records) == sorted(expected_block_ids)
    assert output.most_recent_state.stream_state.__dict__["state"] == {"last_edited_time": "2024-08-01T00:00:00.000000Z"}
