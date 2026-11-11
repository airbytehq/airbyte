# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path
from typing import Any, List, Mapping, Optional

import yaml

from airbyte_cdk.models import AirbyteStateMessage, SyncMode
from airbyte_cdk.sources.declarative.concurrent_declarative_source import ConcurrentDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder, ConfiguredAirbyteStreamBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


_MANIFEST_PATH = Path(__file__).parent.parent.parent / "manifest.yaml"
_CONFIG = {"start_date": "2020-01-01T00:00:00.000Z", "credentials": {"auth_type": "token", "token": "test-token"}}
_SEARCH_URL = "https://api.notion.com/v1/search"
_CHILDREN_URL = "https://api.notion.com/v1/blocks/{}/children"
_PAGES_SEARCH_BODY = {
    "sort": {"direction": "descending", "timestamp": "last_edited_time"},
    "filter": {"property": "object", "value": "page"},
    "page_size": 100,
}


def _block(block_id: str, last_edited_time: str, parent_id: str, has_children: bool = False) -> Mapping[str, Any]:
    return {
        "object": "block",
        "id": block_id,
        "type": "paragraph",
        "paragraph": {"rich_text": []},
        "has_children": has_children,
        "created_time": "2025-01-01T00:00:00.000Z",
        "last_edited_time": last_edited_time,
        "parent": {"type": "page_id", "page_id": parent_id},
    }


def _list_response(results: List[Mapping[str, Any]]) -> HttpResponse:
    return HttpResponse(json.dumps({"object": "list", "results": results, "next_cursor": None, "has_more": False}), 200)


def _children_request(block_id: str) -> HttpRequest:
    return HttpRequest(url=_CHILDREN_URL.format(block_id), query_params={"page_size": "100"})


def _mock_workspace(http_mocker: HttpMocker, page_blocks: List[Mapping[str, Any]], toggle_children: List[Mapping[str, Any]]) -> None:
    page = {"object": "page", "id": "page-1", "last_edited_time": "2026-01-10T00:00:00.000Z", "properties": {}}
    http_mocker.post(HttpRequest(url=_SEARCH_URL, body=json.dumps(_PAGES_SEARCH_BODY)), _list_response([page]))
    http_mocker.get(_children_request("page-1"), _list_response(page_blocks))
    http_mocker.get(_children_request("toggle"), _list_response(toggle_children))


def _read_blocks(state: Optional[List[AirbyteStateMessage]] = None) -> EntrypointOutput:
    stream = ConfiguredAirbyteStreamBuilder().with_name("blocks").with_sync_mode(SyncMode.incremental)
    catalog = CatalogBuilder().with_stream(stream).build()
    source = ConcurrentDeclarativeSource(
        source_config=yaml.safe_load(_MANIFEST_PATH.read_text()), config=_CONFIG, catalog=catalog, state=state
    )
    return read(source, _CONFIG, catalog, state)


def test_incremental_read_emits_only_blocks_edited_since_state_including_nested_children():
    # First sync: no state, every block (including nested children) is emitted and the state is the max cursor value.
    with HttpMocker() as http_mocker:
        _mock_workspace(
            http_mocker,
            page_blocks=[
                _block("old", "2025-06-01T00:00:00.000Z", "page-1"),
                _block("toggle", "2025-06-01T00:00:00.000Z", "page-1", has_children=True),
                _block("recent", "2026-01-05T00:00:00.000Z", "page-1"),
            ],
            toggle_children=[_block("child-old", "2025-06-01T00:00:00.000Z", "toggle")],
        )
        first = _read_blocks()

    assert not first.errors
    assert sorted(r.record.data["id"] for r in first.records) == ["child-old", "old", "recent", "toggle"]
    first_state = first.most_recent_state.stream_state.__dict__
    assert first_state["state"] == {"last_edited_time": "2026-01-05T00:00:00.000000Z"}

    # Second sync with the emitted state: only blocks edited at or after the state value are emitted (the cursor is
    # inclusive, so `recent` is re-emitted as the documented overlap). The `toggle` block itself was not edited, but its
    # newly edited child must still be fetched and emitted.
    with HttpMocker() as http_mocker:
        _mock_workspace(
            http_mocker,
            page_blocks=[
                _block("old", "2025-06-01T00:00:00.000Z", "page-1"),
                _block("toggle", "2025-06-01T00:00:00.000Z", "page-1", has_children=True),
                _block("recent", "2026-01-05T00:00:00.000Z", "page-1"),
                _block("new", "2026-01-07T00:00:00.000Z", "page-1"),
            ],
            toggle_children=[
                _block("child-old", "2025-06-01T00:00:00.000Z", "toggle"),
                _block("child-new", "2026-01-06T00:00:00.000Z", "toggle"),
            ],
        )
        second = _read_blocks(StateBuilder().with_stream_state("blocks", first_state).build())

    assert not second.errors
    assert sorted(r.record.data["id"] for r in second.records) == ["child-new", "new", "recent"]
    assert second.most_recent_state.stream_state.__dict__["state"] == {"last_edited_time": "2026-01-07T00:00:00.000000Z"}
