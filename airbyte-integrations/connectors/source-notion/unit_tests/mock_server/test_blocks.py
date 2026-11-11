# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest

from airbyte_cdk.models import AirbyteMessageSerializer, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from unit_tests.conftest import get_source


CONFIG = {"start_date": "2020-01-01T00:00:00.000Z", "credentials": {"auth_type": "token", "token": "test-token"}}
BASE_URL = "https://api.notion.com/v1/"
OLD = "2024-01-01T00:00:00.000Z"
CUTOFF = "2024-02-01T00:00:00.000Z"
NEW = "2024-03-01T00:00:00.000Z"


def _block(block_id, edited_time, has_children=False):
    return {
        "object": "block",
        "id": block_id,
        "type": "paragraph",
        "paragraph": {"rich_text": []},
        "last_edited_time": edited_time,
        "has_children": has_children,
        "parent": {"type": "page_id", "page_id": "page-id"},
    }


def _response(records):
    return HttpResponse(json.dumps({"object": "list", "results": records, "has_more": False, "next_cursor": None}))


def _read_blocks(blocks, state=None, children=None, second_page_blocks=None, sync_mode=SyncMode.incremental):
    catalog = CatalogBuilder().with_stream("blocks", sync_mode).build()
    with HttpMocker() as http_mocker:
        search = HttpRequest(
            BASE_URL + "search",
            body={
                "sort": {"direction": "descending", "timestamp": "last_edited_time"},
                "filter": {"property": "object", "value": "page"},
                "page_size": 100,
            },
        )
        root = HttpRequest(BASE_URL + "blocks/page-id/children", query_params={"page_size": "100"})
        pages = [{"object": "page", "id": "page-id", "last_edited_time": OLD, "properties": {}}]
        if second_page_blocks is not None:
            pages.append({"object": "page", "id": "second-page", "last_edited_time": OLD, "properties": {}})
        http_mocker.post(search, _response(pages))
        http_mocker.get(root, _response(blocks))
        requests = [search, root]
        if second_page_blocks is not None:
            second_root = HttpRequest(BASE_URL + "blocks/second-page/children", query_params={"page_size": "100"})
            http_mocker.get(second_root, _response(second_page_blocks))
            requests.append(second_root)
        if children is not None:
            nested = HttpRequest(BASE_URL + "blocks/old-parent/children", query_params={"page_size": "100"})
            http_mocker.get(nested, _response(children))
            requests.append(nested)
        output = read(get_source(CONFIG, state), CONFIG, catalog, state=state)
        for request in requests:
            http_mocker.assert_number_of_calls(request, 1)
        request_count = http_mocker._mocker.call_count
        assert request_count == len(requests)
        return output, request_count


@pytest.mark.parametrize("two_pages", [False, True], ids=["one-page", "two-pages"])
def test_blocks_incremental_filters_after_recursion_with_global_cursor(two_pages):
    initial, _ = _read_blocks([_block("seed", CUTOFF)])
    assert not initial.errors
    assert [message.record.data["id"] for message in initial.records] == ["seed"]
    state = [initial.state_messages[-1].state]
    print("INITIAL_STATE:", json.dumps(AirbyteMessageSerializer.dump(initial.state_messages[-1])))
    output, request_count = _read_blocks(
        [_block("old-block", OLD), _block("new-block", NEW), _block("old-parent", OLD, has_children=True)],
        state=state,
        children=[_block("new-child", NEW)],
        second_page_blocks=[_block("second-old-block", OLD), _block("second-new-block", "2024-02-15T00:00:00.000Z")] if two_pages else None,
    )
    assert not output.errors
    ids = [message.record.data["id"] for message in output.records]
    print("INCREMENTAL_RECORD_IDS:", ids)
    print("INCREMENTAL_STATE:", json.dumps(AirbyteMessageSerializer.dump(output.state_messages[-1])))
    print("INCREMENTAL_HTTP_REQUESTS:", request_count)
    expected_ids = {"new-block", "new-child"}
    if two_pages:
        expected_ids.add("second-new-block")
    assert set(ids) == expected_ids
    assert len(ids) == len(expected_ids)
    assert request_count == (4 if two_pages else 3)
    final_state = AirbyteMessageSerializer.dump(output.state_messages[-1])["state"]["stream"]["stream_state"]
    assert final_state["state"]["last_edited_time"] == "2024-03-01T00:00:00.000000Z"


@pytest.mark.parametrize("sync_mode", [SyncMode.incremental, SyncMode.full_refresh])
def test_blocks_without_state_respects_start_date_and_type_filter(sync_mode):
    excluded = _block("excluded", NEW, has_children=True)
    excluded["type"] = "child_page"
    output, _ = _read_blocks(
        [_block("before-start", "2019-01-01T00:00:00.000Z"), _block("old-block", OLD), _block("new-block", NEW), excluded],
        sync_mode=sync_mode,
    )
    assert not output.errors
    assert [message.record.data["id"] for message in output.records] == ["old-block", "new-block"]


def test_blocks_empty_response():
    output, _ = _read_blocks([])
    assert not output.errors
    assert not output.records
