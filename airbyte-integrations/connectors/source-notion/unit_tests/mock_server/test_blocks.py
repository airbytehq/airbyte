# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from unit_tests.conftest import get_source


_CONFIG = {"start_date": "2023-01-01T00:00:00.000Z", "credentials": {"auth_type": "token", "token": "token"}}
_SEARCH_REQUEST = HttpRequest(
    url="https://api.notion.com/v1/search",
    body={
        "sort": {"direction": "descending", "timestamp": "last_edited_time"},
        "filter": {"property": "object", "value": "page"},
        "page_size": 100,
    },
)


def _children_request(block_id):
    return HttpRequest(url=f"https://api.notion.com/v1/blocks/{block_id}/children", query_params={"page_size": "100"})


def _list_response(results):
    return HttpResponse(json.dumps({"object": "list", "results": results, "has_more": False, "next_cursor": None}), 200)


def _page(page_id, last_edited_time):
    return {"object": "page", "id": page_id, "last_edited_time": last_edited_time, "properties": {}}


def _block(block_id, page_id, last_edited_time):
    return {
        "object": "block",
        "id": block_id,
        "type": "paragraph",
        "has_children": False,
        "last_edited_time": last_edited_time,
        "parent": {"type": "page_id", "page_id": page_id},
    }


def _read_blocks(pages, blocks_by_page, state=None):
    """Read `blocks` incrementally; every page's children must be requested exactly once."""
    catalog = CatalogBuilder().with_stream("blocks", SyncMode.incremental).build()
    with HttpMocker() as http_mocker:
        http_mocker.post(_SEARCH_REQUEST, _list_response(pages))
        children_requests = {page_id: _children_request(page_id) for page_id in blocks_by_page}
        for page_id, blocks in blocks_by_page.items():
            http_mocker.get(children_requests[page_id], _list_response(blocks))
        output = read(get_source(_CONFIG, state), _CONFIG, catalog, state)
        for children_request in children_requests.values():
            http_mocker.assert_number_of_calls(children_request, 1)
    assert not output.errors
    return output


def test_first_read_skips_blocks_edited_before_the_start_date():
    output = _read_blocks(
        pages=[_page("page-1", "2024-01-02T00:00:00.000Z")],
        blocks_by_page={
            "page-1": [
                _block("before-start-date", "page-1", "2022-06-01T00:00:00.000Z"),
                _block("after-start-date", "page-1", "2024-01-02T00:00:00.000Z"),
            ]
        },
    )

    assert [record.record.data["id"] for record in output.records] == ["after-start-date"]
    assert output.most_recent_state.stream_state.state == {"last_edited_time": "2024-01-02T00:00:00.000000Z"}


def test_second_read_emits_only_blocks_edited_since_the_saved_cursor():
    first_read = _read_blocks(
        pages=[_page("page-2", "2024-03-01T00:00:00.000Z"), _page("page-1", "2024-01-02T00:00:00.000Z")],
        blocks_by_page={
            "page-1": [
                _block("unchanged", "page-1", "2024-01-01T00:00:00.000Z"),
                _block("edited-later", "page-1", "2024-01-02T00:00:00.000Z"),
            ],
            "page-2": [_block("newest", "page-2", "2024-03-01T00:00:00.000Z")],
        },
    )

    assert sorted(record.record.data["id"] for record in first_read.records) == ["edited-later", "newest", "unchanged"]
    assert first_read.most_recent_state.stream_state.state == {"last_edited_time": "2024-03-01T00:00:00.000000Z"}

    second_read = _read_blocks(
        pages=[_page("page-1", "2024-04-01T00:00:00.000Z"), _page("page-2", "2024-03-01T00:00:00.000Z")],
        blocks_by_page={
            "page-1": [
                _block("unchanged", "page-1", "2024-01-01T00:00:00.000Z"),
                _block("edited-later", "page-1", "2024-04-01T00:00:00.000Z"),
            ],
            "page-2": [_block("newest", "page-2", "2024-03-01T00:00:00.000Z")],
        },
        state=[first_read.state_messages[-1].state],
    )

    # The cursor is inclusive, so the block sitting exactly on the saved cursor is emitted again; "unchanged" is not
    assert sorted(record.record.data["id"] for record in second_read.records) == ["edited-later", "newest"]
    assert second_read.most_recent_state.stream_state.state == {"last_edited_time": "2024-04-01T00:00:00.000000Z"}
