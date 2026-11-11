# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from typing import Any, Dict, List

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


_STREAM_NAME = "blocks"
_CONFIG = {"start_date": "2020-01-01T00:00:00.000Z", "credentials": {"auth_type": "token", "token": "abcd"}}
_HEADERS = {"Authorization": "Bearer abcd", "Notion-Version": "2025-09-03"}
_URL_BASE = "https://api.notion.com/v1"


def _block(block_id: str, last_edited_time: str, has_children: bool = False) -> Dict[str, Any]:
    return {
        "object": "block",
        "id": block_id,
        "parent": {"type": "page_id", "page_id": "page"},
        "created_time": "2021-01-01T00:00:00.000Z",
        "last_edited_time": last_edited_time,
        "has_children": has_children,
        "archived": False,
        "in_trash": False,
        "type": "paragraph",
        "paragraph": {"rich_text": [], "color": "default"},
    }


def _list_response(results: List[Dict[str, Any]]) -> HttpResponse:
    return HttpResponse(json.dumps({"object": "list", "results": results, "next_cursor": None, "has_more": False}), 200)


def _given_pages(http_mocker: HttpMocker, page_ids: List[str]) -> None:
    http_mocker.post(
        HttpRequest(
            url=f"{_URL_BASE}/search",
            headers=_HEADERS,
            body={
                "sort": {"direction": "descending", "timestamp": "last_edited_time"},
                "filter": {"property": "object", "value": "page"},
                "page_size": 100,
            },
        ),
        _list_response(
            [{"object": "page", "id": page_id, "last_edited_time": "2022-06-01T00:00:00.000Z", "properties": {}} for page_id in page_ids]
        ),
    )


def _given_children(http_mocker: HttpMocker, block_id: str, children: List[Dict[str, Any]]) -> None:
    http_mocker.get(
        HttpRequest(url=f"{_URL_BASE}/blocks/{block_id}/children", query_params={"page_size": "100"}, headers=_HEADERS),
        _list_response(children),
    )


def _read(state: Any = None) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
    return read(get_source(_CONFIG, state), _CONFIG, catalog, state)


def _record_ids(output: EntrypointOutput) -> List[str]:
    # Pages are read concurrently, so the order across pages is not deterministic.
    return sorted(record.record.data["id"] for record in output.records)


def test_second_incremental_read_emits_only_blocks_edited_since_the_saved_cursor():
    with HttpMocker() as http_mocker:
        _given_pages(http_mocker, ["page-1", "page-2"])
        _given_children(
            http_mocker,
            "page-1",
            [_block("p1-plain", "2022-01-01T00:00:00.000Z"), _block("p1-toggle", "2022-02-01T00:00:00.000Z", has_children=True)],
        )
        _given_children(http_mocker, "p1-toggle", [_block("p1-nested", "2022-02-01T00:00:00.000Z")])
        _given_children(
            http_mocker,
            "page-2",
            [_block("p2-plain", "2022-01-01T00:00:00.000Z"), _block("p2-toggle", "2022-01-01T00:00:00.000Z", has_children=True)],
        )
        _given_children(http_mocker, "p2-toggle", [_block("p2-nested", "2022-03-01T00:00:00.000Z")])

        first_read = _read()

    assert _record_ids(first_read) == ["p1-nested", "p1-plain", "p1-toggle", "p2-nested", "p2-plain", "p2-toggle"]
    first_state = first_read.most_recent_state.stream_state.__dict__
    assert first_state["state"] == {"last_edited_time": "2022-03-01T00:00:00.000000Z"}

    state = StateBuilder().with_stream_state(_STREAM_NAME, first_state).build()
    with HttpMocker() as http_mocker:
        _given_pages(http_mocker, ["page-1", "page-2"])
        # Between the two syncs, one top-level block and one nested block (inside an untouched toggle) are edited.
        _given_children(
            http_mocker,
            "page-1",
            [_block("p1-plain", "2022-04-01T00:00:00.000Z"), _block("p1-toggle", "2022-02-01T00:00:00.000Z", has_children=True)],
        )
        _given_children(http_mocker, "p1-toggle", [_block("p1-nested", "2022-05-01T00:00:00.000Z")])
        _given_children(
            http_mocker,
            "page-2",
            [_block("p2-plain", "2022-01-01T00:00:00.000Z"), _block("p2-toggle", "2022-01-01T00:00:00.000Z", has_children=True)],
        )
        _given_children(http_mocker, "p2-toggle", [_block("p2-nested", "2022-03-01T00:00:00.000Z")])

        second_read = _read(state)
        # HttpMocker fails the test on exit unless every mocked request was sent: the children of the
        # untouched toggles are still fetched, which is how the edit to `p1-nested` is found.

    # The cursor comparison is inclusive, so `p2-nested`, sitting exactly on the saved cursor, is emitted again.
    # Every other unchanged block is dropped.
    assert _record_ids(second_read) == ["p1-nested", "p1-plain", "p2-nested"]
    assert second_read.most_recent_state.stream_state.__dict__["state"] == {"last_edited_time": "2022-05-01T00:00:00.000000Z"}
