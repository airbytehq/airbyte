# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from typing import Any, Dict, List, Mapping, Optional

from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder, ConfiguredAirbyteStreamBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


_CONFIG = {"credentials": {"auth_type": "token", "token": "test-token"}, "start_date": "2020-01-01T00:00:00.000Z"}
_API = "https://api.notion.com/v1"
_OLD = "2023-01-01T00:00:00.000Z"
_FIRST_SYNC = "2024-06-01T00:00:00.000Z"
_SECOND_SYNC = "2024-09-01T00:00:00.000Z"


def _page(page_id: str, last_edited_time: str) -> Dict[str, Any]:
    return {
        "object": "page",
        "id": page_id,
        "created_time": _OLD,
        "last_edited_time": last_edited_time,
        "parent": {"type": "workspace", "workspace": True},
        "properties": {},
    }


def _block(block_id: str, last_edited_time: str, has_children: bool = False) -> Dict[str, Any]:
    return {
        "object": "block",
        "id": block_id,
        "type": "paragraph",
        "created_time": _OLD,
        "last_edited_time": last_edited_time,
        "has_children": has_children,
        "parent": {"type": "page_id", "page_id": "page-1"},
        "paragraph": {"rich_text": []},
    }


def _results(records: List[Mapping[str, Any]]) -> HttpResponse:
    return HttpResponse(json.dumps({"object": "list", "results": records, "has_more": False, "next_cursor": None}), 200)


def _mock_workspace(http_mocker: HttpMocker, nested_child_last_edited_time: str, new_block_last_edited_time: Optional[str]) -> None:
    http_mocker.post(
        HttpRequest(
            url=f"{_API}/search",
            body={"sort": {"direction": "descending", "timestamp": "last_edited_time"}, "filter": {"property": "object", "value": "page"}, "page_size": 100},
        ),
        _results([_page("page-1", _SECOND_SYNC), _page("page-2", _OLD)]),
    )
    page_1_blocks = [_block("unchanged-parent", _OLD, has_children=True)]
    if new_block_last_edited_time:
        page_1_blocks.append(_block("new-block", new_block_last_edited_time))
    http_mocker.get(HttpRequest(url=f"{_API}/blocks/page-1/children", query_params={"page_size": "100"}), _results(page_1_blocks))
    http_mocker.get(
        HttpRequest(url=f"{_API}/blocks/unchanged-parent/children", query_params={"page_size": "100"}),
        _results([_block("nested-child", nested_child_last_edited_time)]),
    )
    http_mocker.get(HttpRequest(url=f"{_API}/blocks/page-2/children", query_params={"page_size": "100"}), _results([_block("old-block", _OLD)]))


def _read_blocks(state: Optional[Mapping[str, Any]]) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(ConfiguredAirbyteStreamBuilder().with_name("blocks").with_sync_mode(SyncMode.incremental)).build()
    built_state = StateBuilder().with_stream_state("blocks", state).build() if state is not None else StateBuilder().build()
    return read(get_source(_CONFIG, built_state), config=_CONFIG, catalog=catalog, state=built_state)


def test_incremental_read_emits_only_blocks_edited_after_state_including_nested_children() -> None:
    with HttpMocker() as http_mocker:
        _mock_workspace(http_mocker, nested_child_last_edited_time=_OLD, new_block_last_edited_time=_FIRST_SYNC)
        first = _read_blocks(state=None)

    assert sorted(record.record.data["id"] for record in first.records) == ["nested-child", "new-block", "old-block", "unchanged-parent"]
    first_state = first.most_recent_state.stream_state.__dict__
    assert first_state["state"] == {"last_edited_time": "2024-06-01T00:00:00.000000Z"}

    # Second sync: only a nested child of an otherwise unchanged block was edited. Its ancestors keep their old
    # `last_edited_time`, so the child must still be fetched and it must be the only block emitted.
    with HttpMocker() as http_mocker:
        _mock_workspace(http_mocker, nested_child_last_edited_time=_SECOND_SYNC, new_block_last_edited_time=None)
        second = _read_blocks(state=first_state)

    assert not second.errors
    assert [record.record.data["id"] for record in second.records] == ["nested-child"]
    assert second.most_recent_state.stream_state.__dict__["state"] == {"last_edited_time": "2024-09-01T00:00:00.000000Z"}
