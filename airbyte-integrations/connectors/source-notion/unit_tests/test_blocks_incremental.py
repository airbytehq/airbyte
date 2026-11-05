# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest

from airbyte_cdk.models import AirbyteStateMessageSerializer, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


def _response(records):
    return {"object": "list", "results": records, "next_cursor": None, "has_more": False}


def _block(id, edited, has_children=False, block_type="paragraph"):
    return {"object": "block", "id": id, "type": block_type, "last_edited_time": edited, "has_children": has_children}


def _state(output):
    return AirbyteStateMessageSerializer.dump(output.state_messages[-1].state)["stream"]["stream_state"]


def _expected_state(cursor):
    return {
        "state": {"last_edited_time": cursor},
        "use_global_cursor": True,
        "lookback_window": 1,
        "parent_state": {},
    }


@pytest.mark.parametrize("with_state", [True, False], ids=["state", "start-date"])
def test_blocks_incremental_recurses_into_unchanged_parents(requests_mock, with_state):
    cutoff = "2024-06-01T00:00:00.000Z"
    newest = "2024-06-03T00:00:00.000Z"
    config = {"start_date": "2020-01-01T00:00:00.000Z" if with_state else cutoff, "credentials": {"auth_type": "token", "token": "abcd"}}

    requests_mock.post("https://api.notion.com/v1/search", json=_response([{"id": "page-1", "last_edited_time": newest}]))
    requests_mock.get(
        "https://api.notion.com/v1/blocks/page-1/children",
        json=_response(
            [
                _block("old", "2024-05-01T00:00:00.000Z"),
                _block("old-parent", "2024-05-02T00:00:00.000Z", True),
                _block("boundary", cutoff),
                _block("new", "2024-06-02T00:00:00.000Z"),
            ]
        ),
    )
    requests_mock.get("https://api.notion.com/v1/blocks/old-parent/children", json=_response([_block("new-child", newest)]))
    state = StateBuilder().with_stream_state("blocks", _expected_state("2024-06-01T00:00:00.000000Z")).build() if with_state else []
    catalog = CatalogBuilder().with_stream("blocks", SyncMode.incremental).build()
    output = read(get_source(config, state), config=config, catalog=catalog, state=state)
    assert [record.record.data["id"] for record in output.records] == ["new-child", "boundary", "new"]
    assert _state(output) == _expected_state("2024-06-03T00:00:00.000000Z")
    assert not output.errors


def test_blocks_incremental_consecutive_reads(requests_mock):
    start = "2024-06-01T00:00:00.000Z"
    first_max = "2024-06-02T00:00:00.000Z"
    second_max = "2024-06-04T00:00:00.000Z"
    config = {"start_date": start, "credentials": {"auth_type": "token", "token": "abcd"}}
    catalog = CatalogBuilder().with_stream("blocks", SyncMode.incremental).build()
    requests_mock.post("https://api.notion.com/v1/search", json=_response([{"id": "page-1", "last_edited_time": second_max}]))
    unchanged = [_block("before-start", "2024-05-01T00:00:00.000Z"), _block("boundary", start)]
    requests_mock.get(
        "https://api.notion.com/v1/blocks/page-1/children",
        [
            {"json": _response(unchanged + [_block("edited", first_max)])},
            {"json": _response(unchanged + [_block("edited", second_max), _block("added", "2024-06-03T00:00:00.000Z")])},
        ],
    )
    first = read(get_source(config), config=config, catalog=catalog)
    assert [record.record.data["id"] for record in first.records] == ["boundary", "edited"]
    assert _state(first) == _expected_state("2024-06-02T00:00:00.000000Z")
    assert not first.errors

    state = [message.state for message in first.state_messages]
    second = read(get_source(config, state), config=config, catalog=catalog, state=state)
    assert [record.record.data["id"] for record in second.records] == ["edited", "added"]
    assert _state(second) == _expected_state("2024-06-04T00:00:00.000000Z")
    assert not second.errors


@pytest.mark.parametrize("block_type", ["child_page", "child_database", "ai_block"])
def test_blocks_excluded_types_are_not_emitted_or_recursed(requests_mock, block_type):
    edited = "2024-06-02T00:00:00.000Z"
    config = {"start_date": "2024-06-01T00:00:00.000Z", "credentials": {"auth_type": "token", "token": "abcd"}}
    requests_mock.post("https://api.notion.com/v1/search", json=_response([{"id": "page-1", "last_edited_time": edited}]))
    requests_mock.get("https://api.notion.com/v1/blocks/page-1/children", json=_response([_block("excluded", edited, True, block_type)]))
    output = read(get_source(config), config=config, catalog=CatalogBuilder().with_stream("blocks", SyncMode.incremental).build())
    assert not output.records
    assert not output.errors
    assert all("/blocks/excluded/" not in request.url for request in requests_mock.request_history)


@pytest.mark.parametrize("status_code", [200, 400, 404])
def test_blocks_unchanged_parent_with_empty_or_ignored_children(requests_mock, status_code):
    cutoff = "2024-06-01T00:00:00.000000Z"
    config = {"start_date": "2020-01-01T00:00:00.000Z", "credentials": {"auth_type": "token", "token": "abcd"}}
    requests_mock.post("https://api.notion.com/v1/search", json=_response([{"id": "page-1", "last_edited_time": cutoff}]))
    requests_mock.get(
        "https://api.notion.com/v1/blocks/page-1/children", json=_response([_block("old-parent", "2024-05-01T00:00:00.000Z", True)])
    )
    children = requests_mock.get("https://api.notion.com/v1/blocks/old-parent/children", status_code=status_code, json=_response([]))
    state = StateBuilder().with_stream_state("blocks", _expected_state(cutoff)).build()
    catalog = CatalogBuilder().with_stream("blocks", SyncMode.incremental).build()
    output = read(get_source(config, state), config=config, catalog=catalog, state=state)
    assert children.call_count == 1
    assert not output.records
    assert not output.errors
    assert _state(output) == _expected_state(cutoff)
