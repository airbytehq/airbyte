# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest

from airbyte_cdk.models import AirbyteStateMessageSerializer, ConfiguredAirbyteCatalogSerializer
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


CONFIG = {"start_date": "2020-01-01T00:00:00.000Z", "credentials": {"auth_type": "token", "token": "abcd"}}
OLD = "2023-01-01T00:00:00.000Z"
STATE = "2023-06-01T00:00:00.000Z"
NEW = "2023-07-01T00:00:00.000Z"


def block(id, timestamp, has_children=False):
    return {"id": id, "type": "paragraph", "last_edited_time": timestamp, "has_children": has_children}


def response(records):
    return {"object": "list", "results": records, "has_more": False, "next_cursor": None}


def run_read(requests_mock, records, state, nested):
    requests_mock.post(
        "https://api.notion.com/v1/search",
        json=response([{"id": "page", "object": "page", "last_edited_time": "2023-08-01T00:00:00.000Z", "properties": {}}]),
    )
    requests_mock.get("https://api.notion.com/v1/blocks/page/children", json=response(records))
    if nested:
        requests_mock.get(
            "https://api.notion.com/v1/blocks/old/children", json=response([block("child-old", OLD), block("child-new", NEW)])
        )
        requests_mock.get(
            "https://api.notion.com/v1/blocks/new/children", json=response([block("child-old", OLD), block("child-new", NEW)])
        )
    catalog = ConfiguredAirbyteCatalogSerializer.load(
        {
            "streams": [
                {
                    "stream": {"name": "blocks", "json_schema": {}, "supported_sync_modes": ["full_refresh", "incremental"]},
                    "sync_mode": "incremental",
                    "destination_sync_mode": "append",
                }
            ]
        }
    )
    output = read(get_source(CONFIG, state), config=CONFIG, catalog=catalog, state=state)
    output.raise_if_errors()
    return output


@pytest.mark.parametrize("nested", [False, True])
@pytest.mark.parametrize("state_shape", ["legacy", "emitted"])
def test_blocks_incremental_filters_records_and_updates_state(requests_mock, nested, state_shape):
    first = run_read(requests_mock, [block("seed", STATE)], [], False)
    state = (
        [first.state_messages[-1].state]
        if state_shape == "emitted"
        else StateBuilder().with_stream_state("blocks", {"last_edited_time": STATE}).build()
    )
    second = run_read(requests_mock, [block("old", OLD, nested), block("new", NEW, nested)], state, nested)
    ids = [message.record.data["id"] for message in second.records]
    assert ids == (["child-new", "new"] if nested else ["new"])
    emitted_state = AirbyteStateMessageSerializer.dump(second.state_messages[-1].state)["stream"]["stream_state"]
    assert emitted_state["state"]["last_edited_time"] == "2023-07-01T00:00:00.000000Z"
    if nested:
        assert not any("blocks/old/children" in request.url for request in requests_mock.request_history)
        assert any("blocks/new/children" in request.url for request in requests_mock.request_history)


@pytest.mark.parametrize("record_type", ["child_page", "child_database", "ai_block"])
def test_blocks_incremental_preserves_type_filter(requests_mock, record_type):
    record = dict(block("excluded", NEW), type=record_type)
    output = run_read(requests_mock, [record], [], False)
    assert not output.records
