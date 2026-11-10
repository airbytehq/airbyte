# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


_CONFIG = {"start_date": "2020-01-01T00:00:00.000Z", "credentials": {"auth_type": "token", "token": "abcd"}}
_OLD = "2023-01-01T00:00:00.000Z"
_NEW = "2025-01-01T00:00:00.000Z"


def _block(block_id, edited_time, has_children=False):
    return {
        "object": "block",
        "id": block_id,
        "type": "paragraph",
        "last_edited_time": edited_time,
        "has_children": has_children,
        "parent": {"type": "page_id", "page_id": "page-1"},
    }


def _response(records):
    return HttpResponse(json.dumps({"object": "list", "results": records, "has_more": False, "next_cursor": None}))


def _read_blocks(state=None, sync_mode=SyncMode.incremental, records=None):
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
            _response([{"object": "page", "id": "page-1", "last_edited_time": _NEW, "properties": {}}]),
        )
        http_mocker.get(
            HttpRequest(url="https://api.notion.com/v1/blocks/page-1/children", query_params={"page_size": "100"}),
            _response(
                records
                if records is not None
                else [
                    _block("before-start-date", "2019-01-01T00:00:00.000Z"),
                    _block("old-parent", _OLD, has_children=True),
                    _block("new-block", _NEW),
                ]
            ),
        )
        children_request = HttpRequest(url="https://api.notion.com/v1/blocks/old-parent/children", query_params={"page_size": "100"})
        http_mocker.get(
            children_request,
            _response([_block("old-child", _OLD), _block("new-child", "2025-02-01T00:00:00.000Z")]),
        )
        catalog = CatalogBuilder().with_stream("blocks", sync_mode).build()
        output = read(get_source(_CONFIG, state), _CONFIG, catalog, state=state)
        http_mocker.assert_number_of_calls(children_request, 0 if records is not None else 1)
    assert not output.errors
    return output


@pytest.mark.parametrize("lookback_window", [0, 60])
def test_blocks_incremental_filters_old_records_after_recursing(lookback_window):
    incoming_state = {
        "use_global_cursor": True,
        "state": {"last_edited_time": "2024-01-01T00:00:00.000Z"},
        "lookback_window": lookback_window,
        "parent_state": {},
    }
    state = StateBuilder().with_stream_state("blocks", incoming_state).build()
    output = _read_blocks(state)
    print("INCOMING_STATE:", incoming_state)
    print("EMITTED_STATE:", vars(output.most_recent_state.stream_state))
    ids = [record.record.data["id"] for record in output.records]
    print("EMITTED_IDS:", ids)
    assert ids == ["new-child", "new-block"]
    assert vars(output.most_recent_state.stream_state)["state"] == {"last_edited_time": "2025-02-01T00:00:00.000000Z"}
    assert [record.record.data["parent"]["sequence_number"] for record in output.records] == [1, 2]


@pytest.mark.parametrize("sync_mode", [SyncMode.incremental, SyncMode.full_refresh])
def test_blocks_without_state_preserves_records_before_start_date(sync_mode):
    output = _read_blocks(sync_mode=sync_mode)
    assert [record.record.data["id"] for record in output.records] == [
        "before-start-date",
        "old-child",
        "new-child",
        "old-parent",
        "new-block",
    ]
    assert [record.record.data["parent"]["sequence_number"] for record in output.records] == [0, 0, 1, 1, 2]


def test_blocks_incremental_respects_incoming_lookback():
    state = (
        StateBuilder()
        .with_stream_state(
            "blocks",
            {"use_global_cursor": True, "state": {"last_edited_time": "2024-01-01T00:00:00.000Z"}, "lookback_window": 60},
        )
        .build()
    )
    output = _read_blocks(
        state,
        records=[
            _block("outside-lookback", "2023-12-31T23:58:59.000Z"),
            _block("inside-lookback", "2023-12-31T23:59:30.000Z"),
        ],
    )
    assert [record.record.data["id"] for record in output.records] == ["inside-lookback"]


def test_blocks_empty_response():
    assert not _read_blocks(records=[]).records


def test_blocks_retriever_receives_concurrent_cursor():
    state = (
        StateBuilder()
        .with_stream_state("blocks", {"use_global_cursor": True, "state": {"last_edited_time": "2024-01-01T00:00:00.000Z"}})
        .build()
    )
    stream = next(stream for stream in get_source(_CONFIG, state).streams(_CONFIG) if stream.name == "blocks")
    generator = stream._stream_partition_generator
    retriever = generator._partition_factory._retriever
    assert retriever.cursor is generator._stream_slicer
    assert retriever._filter_records is True
