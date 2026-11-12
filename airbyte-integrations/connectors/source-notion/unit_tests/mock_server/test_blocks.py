# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
"""Mock-server read tests for the `blocks` stream (recursive `BlocksRetriever` + client-side incremental sync)."""

import json
from typing import Any, Dict, List, Mapping, Optional

import freezegun

from airbyte_cdk.models import ConfiguredAirbyteCatalogSerializer
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


_CONFIG = {"start_date": "2020-01-01T00:00:00.000Z", "credentials": {"auth_type": "token", "token": "abcd"}}
_BASE_URL = "https://api.notion.com/v1"
_STREAM = "blocks"


def _page(page_id: str, last_edited_time: str) -> Dict[str, Any]:
    return {
        "object": "page",
        "id": page_id,
        "created_time": "2021-01-01T00:00:00.000Z",
        "last_edited_time": last_edited_time,
        "parent": {"type": "workspace", "workspace": True},
        "archived": False,
        "in_trash": False,
        "properties": {},
    }


def _block(block_id: str, last_edited_time: str, parent_id: str, has_children: bool = False) -> Dict[str, Any]:
    return {
        "object": "block",
        "id": block_id,
        "parent": {"type": "page_id", "page_id": parent_id},
        "created_time": "2021-01-01T00:00:00.000Z",
        "last_edited_time": last_edited_time,
        "has_children": has_children,
        "archived": False,
        "in_trash": False,
        "type": "paragraph",
        "paragraph": {"rich_text": []},
    }


def _list_response(results: List[Mapping[str, Any]]) -> HttpResponse:
    return HttpResponse(json.dumps({"object": "list", "results": results, "next_cursor": None, "has_more": False}), 200)


def _mock_workspace(
    http_mocker: HttpMocker, page_edited: str, top_level: List[Mapping[str, Any]], toggle_children: List[Mapping[str, Any]]
) -> None:
    http_mocker.post(
        HttpRequest(
            url=f"{_BASE_URL}/search",
            body={
                "page_size": 100,
                "sort": {"direction": "descending", "timestamp": "last_edited_time"},
                "filter": {"property": "object", "value": "page"},
            },
        ),
        _list_response([_page("page-1", page_edited)]),
    )
    http_mocker.get(
        HttpRequest(url=f"{_BASE_URL}/blocks/page-1/children", query_params={"page_size": "100"}),
        _list_response(top_level),
    )
    http_mocker.get(
        HttpRequest(url=f"{_BASE_URL}/blocks/toggle/children", query_params={"page_size": "100"}),
        _list_response(toggle_children),
    )


def _read(state: Optional[Mapping[str, Any]] = None) -> EntrypointOutput:
    catalog = ConfiguredAirbyteCatalogSerializer.load(
        {
            "streams": [
                {
                    "stream": {"name": _STREAM, "json_schema": {}, "supported_sync_modes": ["full_refresh", "incremental"]},
                    "sync_mode": "incremental",
                    "destination_sync_mode": "append",
                }
            ]
        }
    )
    built_state = StateBuilder().with_stream_state(_STREAM, state).build() if state is not None else StateBuilder().build()
    return read(get_source(_CONFIG, built_state), config=_CONFIG, catalog=catalog, state=built_state)


@freezegun.freeze_time("2024-07-01T00:00:00Z")
def test_incremental_read_emits_only_blocks_edited_since_state_including_nested_children() -> None:
    """
    The first read emits the whole block tree and checkpoints the latest `last_edited_time`. The second read, made with
    that state, must only emit blocks edited after it: unchanged top-level and nested blocks are dropped, while an
    edited child of an unchanged parent block is still found (the parent is still traversed) and emitted.
    """
    first_sync = "2024-01-01T00:00:00.000Z"
    with HttpMocker() as http_mocker:
        _mock_workspace(
            http_mocker,
            page_edited=first_sync,
            top_level=[
                _block("unchanged", "2023-06-01T00:00:00.000Z", "page-1"),
                _block("latest", first_sync, "page-1"),
                _block("toggle", "2023-06-01T00:00:00.000Z", "page-1", has_children=True),
            ],
            toggle_children=[
                _block("unchanged-child", "2023-06-01T00:00:00.000Z", "toggle"),
                _block("child-to-edit", "2023-06-01T00:00:00.000Z", "toggle"),
            ],
        )
        first = _read()

    assert sorted(r.record.data["id"] for r in first.records) == ["child-to-edit", "latest", "toggle", "unchanged", "unchanged-child"]
    first_state = first.most_recent_state.stream_state.__dict__
    assert first_state["state"] == {"last_edited_time": "2024-01-01T00:00:00.000000Z"}

    edit_time = "2024-06-01T00:00:00.000Z"
    with HttpMocker() as http_mocker:
        _mock_workspace(
            http_mocker,
            page_edited=edit_time,
            top_level=[
                _block("unchanged", "2023-06-01T00:00:00.000Z", "page-1"),
                _block("latest", first_sync, "page-1"),
                _block("new-block", edit_time, "page-1"),
                _block("toggle", "2023-06-01T00:00:00.000Z", "page-1", has_children=True),
            ],
            toggle_children=[
                _block("unchanged-child", "2023-06-01T00:00:00.000Z", "toggle"),
                _block("child-to-edit", edit_time, "toggle"),
            ],
        )
        second = _read(first_state)

    # `latest` is re-emitted: the cursor is inclusive of the checkpointed value (documented overlap). Nothing older is.
    assert sorted(r.record.data["id"] for r in second.records) == ["child-to-edit", "latest", "new-block"]
    assert second.most_recent_state.stream_state.__dict__["state"] == {"last_edited_time": "2024-06-01T00:00:00.000000Z"}
