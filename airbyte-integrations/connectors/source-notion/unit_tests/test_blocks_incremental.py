# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
from freezegun import freeze_time

from airbyte_cdk.models import AirbyteStateMessageSerializer, ConfiguredAirbyteCatalogSerializer
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


CURSOR = "2024-06-01T00:00:00.000Z"
OLD = "2024-01-01T00:00:00.000Z"


@freeze_time("2024-07-01")
@pytest.mark.parametrize(
    "initial_state,lookback,empty,status_code,expected_ids",
    [
        (True, 0, False, 200, ["container", "equal", "nested-new"]),
        (True, 60, False, 200, ["container", "equal", "lookback", "nested-new"]),
        (False, 0, False, 200, ["container", "equal", "lookback", "nested-new", "nested-old", "old"]),
        (True, 0, True, 200, []),
        (True, 0, False, 404, []),
    ],
)
def test_blocks_incremental_read(requests_mock, initial_state, lookback, empty, status_code, expected_ids):
    config = {"credentials": {"auth_type": "token", "token": "mock"}, "num_workers": 1}
    stream_state = (
        {"state": {"last_edited_time": CURSOR}, "use_global_cursor": True, "lookback_window": lookback, "parent_state": {}}
        if initial_state
        else {}
    )
    state = StateBuilder().with_stream_state("blocks", stream_state).build()
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

    def response(records):
        return {"object": "list", "results": records, "has_more": False, "next_cursor": None}

    def block(block_id, edited, has_children=False, block_type="paragraph"):
        return {"id": block_id, "type": block_type, "last_edited_time": edited, "has_children": has_children}

    requests_mock.post("https://api.notion.com/v1/search", json=response([{"id": "page", "object": "page", "last_edited_time": CURSOR}]))
    blocks = [
        block("old", OLD),
        block("equal", CURSOR),
        block("lookback", "2024-05-31T23:59:30.000Z"),
        block("container", CURSOR, True),
        block("excluded", CURSOR, block_type="child_page"),
        block("before-start", "2020-01-01T00:00:00.000Z"),
    ]
    requests_mock.get(
        "https://api.notion.com/v1/blocks/page/children",
        json=response([] if empty else blocks),
        status_code=status_code,
    )
    requests_mock.get(
        "https://api.notion.com/v1/blocks/container/children",
        json=response([block("nested-old", OLD), block("nested-new", CURSOR)]),
    )

    output = read(get_source(config, state), config=config, catalog=catalog, state=state)
    output.raise_if_errors()
    assert sorted(record.record.data["id"] for record in output.records) == expected_ids
    emitted_state = AirbyteStateMessageSerializer.dump(output.state_messages[-1].state)["stream"]["stream_state"]
    assert emitted_state == {
        "state": {"last_edited_time": "2024-06-01T00:00:00.000000Z"},
        "use_global_cursor": True,
        "parent_state": {},
        "lookback_window": 0 if expected_ids else lookback,
    }
