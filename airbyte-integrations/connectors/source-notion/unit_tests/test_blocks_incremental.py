# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest

from airbyte_cdk.models import AirbyteMessageSerializer, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


CONFIG = {"start_date": "2020-01-01T00:00:00.000Z", "credentials": {"auth_type": "token", "token": "abcd"}}
CURSOR = "2024-01-02T00:00:00.000Z"
NEW_CURSOR = "2024-01-03T00:00:00.000Z"


def _response(records):
    return HttpResponse(json.dumps({"object": "list", "results": records, "has_more": False, "next_cursor": None}))


def _block(id, edited, has_children=False):
    return {"object": "block", "id": id, "type": "paragraph", "last_edited_time": edited, "has_children": has_children}


def test_blocks_incremental_traverses_unchanged_parents():
    state = StateBuilder().with_stream_state("blocks", {"last_edited_time": CURSOR}).build()
    catalog = CatalogBuilder().with_stream("blocks", SyncMode.incremental).build()
    with HttpMocker() as http:
        http.post(
            HttpRequest(
                "https://api.notion.com/v1/search",
                body={
                    "page_size": 100,
                    "sort": {"direction": "descending", "timestamp": "last_edited_time"},
                    "filter": {"property": "object", "value": "page"},
                },
            ),
            _response([{"object": "page", "id": "page-1", "last_edited_time": NEW_CURSOR, "properties": {}}]),
        )
        http.get(
            HttpRequest("https://api.notion.com/v1/blocks/page-1/children?page_size=100"),
            _response([_block("old-parent", "2024-01-01T00:00:00.000Z", True), _block("boundary", CURSOR), _block("new", NEW_CURSOR)]),
        )
        http.get(
            HttpRequest("https://api.notion.com/v1/blocks/old-parent/children?page_size=100"),
            _response([_block("new-child", NEW_CURSOR)]),
        )
        output = read(get_source(CONFIG, state), CONFIG, catalog, state=state)

    assert not output.errors
    assert [record.record.data["id"] for record in output.records] == ["new-child", "boundary", "new"]
    assert output.most_recent_state.stream_state.__dict__["state"]["last_edited_time"] == "2024-01-03T00:00:00.000000Z"


def _round_trip_read(state=None, sync_mode=SyncMode.incremental, child_response=None):
    catalog = CatalogBuilder().with_stream("blocks", sync_mode).build()
    with HttpMocker() as http:
        http.post(
            HttpRequest(
                "https://api.notion.com/v1/search",
                body={
                    "page_size": 100,
                    "sort": {"direction": "descending", "timestamp": "last_edited_time"},
                    "filter": {"property": "object", "value": "page"},
                },
            ),
            _response([{"object": "page", "id": "page-1", "last_edited_time": NEW_CURSOR, "properties": {}}]),
        )
        http.get(
            HttpRequest("https://api.notion.com/v1/blocks/page-1/children?page_size=100"),
            _response(
                [_block("old", CURSOR), _block("parent", NEW_CURSOR, True), _block("boundary", NEW_CURSOR)]
                + [
                    dict(_block(block_type, NEW_CURSOR, True), type=block_type)
                    for block_type in ["child_page", "child_database", "ai_block"]
                ]
            ),
        )
        http.get(
            HttpRequest("https://api.notion.com/v1/blocks/parent/children?page_size=100"),
            child_response if child_response is not None else _response([_block("child", CURSOR)]),
        )
        output = read(get_source(CONFIG, state), CONFIG, catalog, state=state)
    return output


@pytest.mark.parametrize("state_shape", ["emitted", "legacy"])
def test_blocks_incremental_two_sync_round_trip(state_shape):
    first = _round_trip_read()
    assert not first.errors
    assert [record.record.data["id"] for record in first.records] == ["old", "child", "parent", "boundary"]
    final_message = next(message for message in reversed(first.state_messages) if message.state.stream.stream_descriptor.name == "blocks")
    print("FIRST_STATE " + json.dumps(AirbyteMessageSerializer.dump(final_message), sort_keys=True))
    state = [final_message.state]
    if state_shape == "legacy":
        state = StateBuilder().with_stream_state("blocks", {"last_edited_time": NEW_CURSOR}).build()
    second = _round_trip_read(state)
    records = [record.record.data for record in second.records]
    print("SECOND_RECORDS " + state_shape + " " + json.dumps(records, sort_keys=True))
    assert not second.errors
    assert all(record["last_edited_time"] == NEW_CURSOR for record in records)


def test_blocks_full_refresh_preserves_children_and_type_exclusions():
    output = _round_trip_read(sync_mode=SyncMode.full_refresh)
    assert not output.errors
    assert [record.record.data["id"] for record in output.records] == ["old", "child", "parent", "boundary"]


@pytest.mark.parametrize("child_response", [_response([]), HttpResponse('{"object": "error", "code": "object_not_found"}', 404)])
def test_blocks_empty_or_inaccessible_children(child_response):
    output = _round_trip_read(child_response=child_response)
    assert not output.errors
    assert [record.record.data["id"] for record in output.records] == ["old", "parent", "boundary"]
