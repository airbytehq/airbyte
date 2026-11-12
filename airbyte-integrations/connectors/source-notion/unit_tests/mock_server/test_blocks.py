# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from typing import Any, List, Mapping

from airbyte_cdk.models import AirbyteStateBlob, AirbyteStateMessage, AirbyteStateType, AirbyteStreamState, StreamDescriptor, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from unit_tests.conftest import get_source


_CONFIG = {"start_date": "2021-01-01T00:00:00.000Z", "credentials": {"auth_type": "token", "token": "abcd"}}
_STREAM = "blocks"
_API = "https://api.notion.com/v1"


def _block(block_id: str, last_edited_time: str, has_children: bool = False) -> Mapping[str, Any]:
    return {
        "object": "block",
        "id": block_id,
        "parent": {"type": "page_id", "page_id": "page-1"},
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


def _mock_workspace(http_mocker: HttpMocker, toggle: str, toggle_child: str, paragraph: str, quote: str) -> None:
    """One page whose children are a toggle (with one nested child), a paragraph and a quote."""
    http_mocker.post(
        HttpRequest(
            url=f"{_API}/search",
            body={
                "sort": {"direction": "descending", "timestamp": "last_edited_time"},
                "filter": {"property": "object", "value": "page"},
                "page_size": 100,
            },
        ),
        _list_response([{"object": "page", "id": "page-1", "last_edited_time": "2021-12-01T00:00:00.000Z", "properties": {}}]),
    )
    http_mocker.get(
        HttpRequest(url=f"{_API}/blocks/page-1/children", query_params={"page_size": "100"}),
        _list_response([_block("toggle", toggle, has_children=True), _block("paragraph", paragraph), _block("quote", quote)]),
    )
    http_mocker.get(
        HttpRequest(url=f"{_API}/blocks/toggle/children", query_params={"page_size": "100"}),
        _list_response([_block("toggle-child", toggle_child)]),
    )


def _read(state: List[AirbyteStateMessage]) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(_STREAM, SyncMode.incremental).build()
    return read(get_source(_CONFIG, state), config=_CONFIG, catalog=catalog, state=state)


def test_incremental_read_with_previous_state_emits_only_blocks_edited_since_the_cursor():
    """
    The first sync has no state and emits every block, including "paragraph" which was last edited before `start_date`.
    The second sync uses the state the first one emitted and only emits what changed since then.
    """
    with HttpMocker() as http_mocker:
        _mock_workspace(
            http_mocker,
            toggle="2021-10-01T00:00:00.000Z",
            toggle_child="2021-10-10T00:00:00.000Z",
            paragraph="2020-06-01T00:00:00.000Z",
            quote="2021-10-19T00:00:00.000Z",
        )
        first = _read([])

    assert [r.record.data["id"] for r in first.records] == ["toggle-child", "toggle", "paragraph", "quote"]
    first_state = first.most_recent_state.stream_state.__dict__
    assert first_state["state"] == {"last_edited_time": "2021-10-19T00:00:00.000000Z"}

    second_state = [
        AirbyteStateMessage(
            type=AirbyteStateType.STREAM,
            stream=AirbyteStreamState(stream_descriptor=StreamDescriptor(name=_STREAM), stream_state=AirbyteStateBlob(**first_state)),
        )
    ]
    with HttpMocker() as http_mocker:
        # Only the nested child and nothing else changed since the first sync.
        _mock_workspace(
            http_mocker,
            toggle="2021-10-01T00:00:00.000Z",
            toggle_child="2021-12-01T00:00:00.000Z",
            paragraph="2020-06-01T00:00:00.000Z",
            quote="2021-10-19T00:00:00.000Z",
        )
        second = _read(second_state)

    # Unchanged blocks are dropped. The child edited under an unchanged toggle is still fetched and emitted.
    # "quote" sits exactly on the cursor value, which the inclusive client-side cursor re-emits by design.
    assert [r.record.data["id"] for r in second.records] == ["toggle-child", "quote"]
    assert second.most_recent_state.stream_state.__dict__["state"] == {"last_edited_time": "2021-12-01T00:00:00.000000Z"}
