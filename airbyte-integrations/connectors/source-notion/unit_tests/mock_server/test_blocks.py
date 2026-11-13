# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from unit_tests.conftest import get_source

from airbyte_cdk.models import AirbyteMessageSerializer, ConfiguredAirbyteCatalogSerializer
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


_CONFIG = {"start_date": "2020-01-01T00:00:00.000Z", "credentials": {"auth_type": "token", "token": "abcd"}}
_OLD = "2023-01-01T00:00:00.000Z"
_CURSOR = "2023-06-01T00:00:00.000000Z"
_NEW = "2023-07-01T00:00:00.000Z"


def _block(name, timestamp, has_children=False):
    return {
        "id": name,
        "object": "block",
        "type": "paragraph",
        "has_children": has_children,
        "last_edited_time": timestamp,
        "parent": {"type": "page_id", "page_id": "page-id"},
    }


def _read_blocks(blocks, children=None, with_state=True, sync_mode="incremental", start_date=None):
    config = dict(_CONFIG, start_date=start_date or _CONFIG["start_date"])
    state = (
        StateBuilder()
        .with_stream_state(
            "blocks",
            {
                "use_global_cursor": True,
                "state": {"last_edited_time": _CURSOR},
                "lookback_window": 0,
                "parent_state": {},
            }
            if with_state
            else {},
        )
        .build()
    )
    catalog = ConfiguredAirbyteCatalogSerializer.load(
        {
            "streams": [
                {
                    "stream": {"name": "blocks", "json_schema": {}, "supported_sync_modes": ["full_refresh", "incremental"]},
                    "sync_mode": sync_mode,
                    "destination_sync_mode": "append",
                }
            ]
        }
    )
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
            HttpResponse(
                body=json.dumps(
                    {"results": [{"id": "page-id", "object": "page", "last_edited_time": _NEW}], "has_more": False, "next_cursor": None}
                )
            ),
        )
        for parent_id, records in {"page-id": blocks, **(children or {})}.items():
            http_mocker.get(
                HttpRequest(url=f"https://api.notion.com/v1/blocks/{parent_id}/children", query_params={"page_size": "100"}),
                HttpResponse(body=json.dumps({"results": records, "has_more": False, "next_cursor": None})),
            )
        return read(get_source(config, state), config=config, catalog=catalog, state=state)


@pytest.mark.parametrize(
    "blocks,children,expected,final_cursor",
    [
        ([_block("old", _OLD), _block("new", _NEW)], {}, ["new"], _NEW),
        ([_block("parent", _OLD, True)], {"parent": [_block("child", _NEW)]}, ["child"], _NEW),
        ([_block("parent", _NEW, True)], {"parent": [_block("child", _OLD)]}, ["parent"], _NEW),
        ([_block("equal", "2023-06-01T00:00:00.000Z")], {}, ["equal"], _CURSOR),
        ([_block("old", _OLD)], {}, [], _CURSOR),
        ([], {}, [], _CURSOR),
    ],
    ids=["siblings", "old-parent-new-child", "new-parent-old-child", "equal-cursor", "all-old", "empty"],
)
def test_blocks_incremental_filters_records(blocks, children, expected, final_cursor):
    output = _read_blocks(blocks, children)
    assert [message.record.data["id"] for message in output.records] == expected
    state = AirbyteMessageSerializer.dump(output.state_messages[-1])["state"]["stream"]["stream_state"]
    assert state["use_global_cursor"] is True
    assert state["state"]["last_edited_time"] == final_cursor.replace(".000Z", ".000000Z")


@pytest.mark.parametrize(
    "sync_mode,with_state,start_date,expected",
    [
        ("incremental", False, None, ["child", "parent", "new"]),
        ("full_refresh", False, None, ["child", "parent", "new"]),
        ("incremental", False, "2023-06-01T00:00:00.000Z", ["child", "new"]),
    ],
)
def test_blocks_initial_and_full_refresh(sync_mode, with_state, start_date, expected):
    output = _read_blocks(
        [_block("parent", _OLD, True), _block("new", _NEW)], {"parent": [_block("child", _NEW)]}, with_state, sync_mode, start_date
    )
    assert [message.record.data["id"] for message in output.records] == expected
