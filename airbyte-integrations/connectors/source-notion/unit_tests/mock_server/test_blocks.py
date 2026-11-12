#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#
import json

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


_CONFIG = {"start_date": "2020-01-01T00:00:00.000Z", "credentials": {"auth_type": "token", "token": "abcd"}}
_STREAM = "blocks"
_OLD = "2021-10-19T13:33:00.000Z"
_PAGES_SEARCH_BODY = {
    "sort": {"direction": "descending", "timestamp": "last_edited_time"},
    "filter": {"property": "object", "value": "page"},
    "page_size": 100,
}


def _list_response(results):
    return HttpResponse(json.dumps({"object": "list", "results": results, "next_cursor": None, "has_more": False}), 200)


def _block(block_id, last_edited_time, has_children=False):
    return {
        "object": "block",
        "id": block_id,
        "parent": {"type": "page_id", "page_id": "page-1"},
        "created_time": _OLD,
        "last_edited_time": last_edited_time,
        "has_children": has_children,
        "type": "paragraph",
        "paragraph": {"rich_text": []},
    }


def _mock_workspace(http_mocker, child_3_last_edited_time):
    http_mocker.post(
        HttpRequest(url="https://api.notion.com/v1/search", body=json.dumps(_PAGES_SEARCH_BODY)),
        _list_response([{"object": "page", "id": "page-1", "last_edited_time": "2021-12-02T00:00:00.000Z", "properties": {}}]),
    )
    http_mocker.get(
        HttpRequest(url="https://api.notion.com/v1/blocks/page-1/children", query_params={"page_size": "100"}),
        _list_response([_block("block-1", _OLD), _block("block-2", _OLD, has_children=True)]),
    )
    http_mocker.get(
        HttpRequest(url="https://api.notion.com/v1/blocks/block-2/children", query_params={"page_size": "100"}),
        _list_response([_block("block-3", child_3_last_edited_time), _block("block-4", "2021-11-20T00:00:00.000Z")]),
    )


def _read(state):
    catalog = CatalogBuilder().with_stream(_STREAM, SyncMode.incremental).build()
    return read(get_source(_CONFIG, state), config=_CONFIG, catalog=catalog, state=state)


def test_incremental_read_emits_only_blocks_edited_since_the_previous_sync():
    with HttpMocker() as http_mocker:
        _mock_workspace(http_mocker, child_3_last_edited_time="2021-10-20T00:00:00.000Z")
        first = _read(StateBuilder().build())

    assert [record.record.data["id"] for record in first.records] == ["block-1", "block-3", "block-4", "block-2"]
    first_state = first.most_recent_state.stream_state.__dict__
    assert first_state["state"] == {"last_edited_time": "2021-11-20T00:00:00.000000Z"}

    with HttpMocker() as http_mocker:
        _mock_workspace(http_mocker, child_3_last_edited_time="2021-12-01T00:00:00.000Z")
        second = _read(StateBuilder().with_stream_state(_STREAM, first_state).build())

    # block-3 was edited under an unchanged parent; block-4 sits on the inclusive cursor boundary.
    assert [record.record.data["id"] for record in second.records] == ["block-3", "block-4"]
    assert second.most_recent_state.stream_state.__dict__["state"] == {"last_edited_time": "2021-12-01T00:00:00.000000Z"}
