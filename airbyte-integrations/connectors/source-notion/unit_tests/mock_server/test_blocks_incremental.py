# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from freezegun import freeze_time
from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


_CONFIG = {"start_date": "2020-01-01T00:00:00.000Z", "credentials": {"auth_type": "token", "token": "test-token"}}
_CURSOR = "2024-01-02T00:00:00.000Z"
_CHANGED = "2024-01-03T00:00:00.000Z"


def _block(block_id, edited_time, has_children=False, block_type="paragraph"):
    return {"id": block_id, "last_edited_time": edited_time, "type": block_type, "has_children": has_children}


def _response(records):
    return HttpResponse(body=json.dumps({"object": "list", "results": records, "has_more": False, "next_cursor": None}), status_code=200)


@freeze_time("2024-01-04T00:00:00Z")
@pytest.mark.parametrize(
    "sync_mode,prior_state",
    [
        pytest.param(SyncMode.incremental, {"last_edited_time": _CURSOR}, id="legacy-state"),
        pytest.param(SyncMode.incremental, {"use_global_cursor": True, "state": {"last_edited_time": _CURSOR}}, id="global-state"),
        pytest.param(SyncMode.full_refresh, {}, id="full-refresh"),
    ],
)
@pytest.mark.parametrize("scenario", ["siblings", "nested", "empty", "not-found"])
def test_blocks_read_filters_after_traversal_and_preserves_state(sync_mode, prior_state, scenario):
    old = _block("old", "2024-01-01T00:00:00.000Z", has_children=scenario == "nested")
    changed = _block("changed", _CHANGED)
    boundary = _block("boundary", _CURSOR)
    before_start = _block("before-start", "2019-01-01T00:00:00.000Z")
    excluded = [_block(block_type, _CHANGED, block_type=block_type) for block_type in ["child_page", "child_database", "ai_block"]]
    records = [old, boundary, before_start, *excluded] if scenario == "nested" else [old, changed, boundary, before_start, *excluded]
    state = StateBuilder().with_stream_state("blocks", prior_state).build()
    catalog = CatalogBuilder().with_stream("blocks", sync_mode).build()

    with HttpMocker() as http_mocker:
        http_mocker.post(
            HttpRequest(
                url="https://api.notion.com/v1/search",
                body={
                    "sort": {"direction": "descending", "timestamp": "last_edited_time"},
                    "filter": {"property": "object", "value": "page"},
                    "page_size": 100,
                },
            ),
            _response([{"id": "page-1", "last_edited_time": _CHANGED}]),
        )
        http_mocker.get(
            HttpRequest(url="https://api.notion.com/v1/blocks/page-1/children", query_params={"page_size": "100"}),
            HttpResponse(body=json.dumps({"object": "error", "code": "object_not_found", "message": "Not found"}), status_code=404)
            if scenario == "not-found"
            else _response([] if scenario == "empty" else records),
        )
        if scenario == "nested":
            http_mocker.get(
                HttpRequest(url="https://api.notion.com/v1/blocks/old/children", query_params={"page_size": "100"}),
                _response([changed, _block("old-child", old["last_edited_time"])]),
            )

        output = read(get_source(_CONFIG, state), config=_CONFIG, catalog=catalog, state=state)

    assert not output.errors
    expected_ids = ["changed", "boundary"]
    if sync_mode == SyncMode.full_refresh:
        expected_ids = ["changed", "old-child", "old", "boundary"] if scenario == "nested" else ["old", "changed", "boundary"]
    if scenario in ["empty", "not-found"]:
        expected_ids = []
    assert [record.record.data["id"] for record in output.records] == expected_ids
    final_state = output.state_messages[-1].state.stream.stream_state.__dict__
    assert final_state["use_global_cursor"] is True
    if expected_ids:
        assert final_state["state"]["last_edited_time"] == "2024-01-03T00:00:00.000000Z"
    elif prior_state:
        assert final_state["state"]["last_edited_time"] == "2024-01-02T00:00:00.000000Z"
