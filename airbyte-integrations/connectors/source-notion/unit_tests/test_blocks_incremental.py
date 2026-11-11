# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest

from airbyte_cdk.models import ConfiguredAirbyteCatalogSerializer
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source

CONFIG = {"start_date": "2023-06-01T00:00:00.000Z", "credentials": {"auth_type": "token", "token": "abcd"}}
OLD = "2023-01-01T00:00:00.000Z"
BOUNDARY = "2023-06-01T00:00:00.000Z"
NEW = "2023-07-01T00:00:00.000Z"


def block(id, edited, has_children=False):
    return {"id": id, "type": "paragraph", "last_edited_time": edited, "has_children": has_children}


def response(records):
    return HttpResponse(json.dumps({"object": "list", "results": records, "has_more": False, "next_cursor": None}))


@pytest.mark.parametrize(
    "initial_state",
    [
        {"last_edited_time": BOUNDARY},
        {"state": {"last_edited_time": BOUNDARY}, "use_global_cursor": True, "parent_state": {}, "lookback_window": 0},
        {},
    ],
    ids=["legacy-state", "global-state", "first-sync"],
)
@pytest.mark.parametrize("case", ["mixed", "all-old", "empty", "not-found"])
def test_blocks_incremental_filters_nested_records(initial_state, case):
    config = dict(CONFIG, start_date="2020-01-01T00:00:00.000Z") if initial_state else CONFIG
    state = StateBuilder().with_stream_state("blocks", initial_state).build()
    catalog = ConfiguredAirbyteCatalogSerializer.load(
        {
            "streams": [
                {
                    "stream": {"name": "blocks", "json_schema": {}, "supported_sync_modes": ["incremental"]},
                    "sync_mode": "incremental",
                    "destination_sync_mode": "append",
                }
            ]
        }
    )
    with HttpMocker() as http:
        http.post(
            HttpRequest(
                "https://api.notion.com/v1/search",
                body={
                    "sort": {"direction": "descending", "timestamp": "last_edited_time"},
                    "filter": {"property": "object", "value": "page"},
                    "page_size": 100,
                },
            ),
            response([{"id": "page", "last_edited_time": NEW}]),
        )
        root_records = [block("old-parent", OLD, True), block("boundary", BOUNDARY), block("new", NEW)]
        if case == "all-old":
            root_records = [block("old-parent", OLD, True)]
        elif case in ("empty", "not-found"):
            root_records = []
        http.get(
            HttpRequest("https://api.notion.com/v1/blocks/page/children", query_params={"page_size": 100}),
            (
                HttpResponse('{"object": "error", "code": "object_not_found"}', status_code=404)
                if case == "not-found"
                else response(root_records)
            ),
        )
        http.get(
            HttpRequest("https://api.notion.com/v1/blocks/old-parent/children", query_params={"page_size": 100}),
            response([block("old-child", OLD), block("new-child", NEW)] if case == "mixed" else [block("old-child", OLD)]),
        )
        output = read(get_source(config, state), config=config, catalog=catalog, state=state)
    assert [message.record.data["id"] for message in output.records] == (["new-child", "boundary", "new"] if case == "mixed" else [])
    expected_state = {
        "use_global_cursor": True,
        "parent_state": {},
        "lookback_window": 1 if case == "mixed" else 0,
    }
    if case == "mixed" or initial_state:
        expected_state["state"] = {"last_edited_time": (NEW if case == "mixed" else BOUNDARY).replace(".000Z", ".000000Z")}
    assert output.most_recent_state.stream_state.__dict__ == expected_state
