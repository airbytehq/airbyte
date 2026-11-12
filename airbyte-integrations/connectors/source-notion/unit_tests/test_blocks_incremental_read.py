# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest

from airbyte_cdk.models import AirbyteMessageSerializer, ConfiguredAirbyteCatalogSerializer
from airbyte_cdk.test.entrypoint_wrapper import read
from unit_tests.conftest import get_source


@pytest.mark.parametrize("sync_mode", ["incremental", "full_refresh"])
def test_blocks_read_round_trip_state(requests_mock, sync_mode):
    config = {
        "start_date": "2020-01-01T00:00:00.000Z",
        "credentials": {"auth_type": "token", "token": "abcd"},
        "num_workers": 1,
    }
    catalog = ConfiguredAirbyteCatalogSerializer.load(
        {
            "streams": [
                {
                    "stream": {"name": "blocks", "json_schema": {}, "supported_sync_modes": ["full_refresh", "incremental"]},
                    "sync_mode": sync_mode,
                    "cursor_field": ["last_edited_time"],
                    "destination_sync_mode": "append",
                }
            ]
        }
    )
    old = "2022-01-01T00:00:00.000Z"
    cursor = "2022-01-03T00:00:00.000Z"
    newer = "2022-01-04T00:00:00.000Z"

    def block(identifier, edited, has_children=False, block_type="paragraph"):
        return {
            "object": "block",
            "id": identifier,
            "type": block_type,
            "last_edited_time": edited,
            "has_children": has_children,
        }

    def response(records):
        return {"object": "list", "results": records, "has_more": False, "next_cursor": None}

    pages = [{"object": "page", "id": page, "last_edited_time": old, "properties": {}} for page in ["page-1", "page-2"]]
    search = requests_mock.post("https://api.notion.com/v1/search", json=response(pages))
    page_one = requests_mock.get(
        "https://api.notion.com/v1/blocks/page-1/children",
        json=response([block("old-top", old), block("at-cursor", cursor), block("parent", cursor, True)]),
    )
    children = requests_mock.get(
        "https://api.notion.com/v1/blocks/parent/children",
        [
            {"json": response([block("old-child", old)])},
            {"json": response([block("old-child", old), block("new-child", newer)])},
        ],
    )
    page_two = requests_mock.get(
        "https://api.notion.com/v1/blocks/page-2/children",
        [
            {"json": response([block("second-page-old", old)])},
            {"json": response([block("second-page-old", old), block("new", newer), block("excluded", newer, block_type="child_page")])},
        ],
    )

    first = read(get_source(config), config=config, catalog=catalog)
    first.raise_if_errors()
    initial_ids = ["at-cursor", "old-child", "old-top", "parent", "second-page-old"]
    assert sorted(message.record.data["id"] for message in first.records) == initial_ids
    state_message = [message for message in first.state_messages if message.state.stream.stream_descriptor.name == "blocks"][-1]
    state = [state_message.state]
    if sync_mode == "full_refresh":
        # Airbyte clears incremental state before starting a full-refresh job.
        state = []
    if sync_mode == "incremental":
        assert AirbyteMessageSerializer.dump(state_message)["state"]["stream"]["stream_state"]["state"] == {
            "last_edited_time": "2022-01-03T00:00:00.000000Z"
        }

    second = read(get_source(config, state), config=config, catalog=catalog, state=state)
    second.raise_if_errors()
    expected_ids = ["at-cursor", "new", "new-child", "parent"]
    if sync_mode == "full_refresh":
        expected_ids = sorted(initial_ids + ["new", "new-child"])
    assert sorted(message.record.data["id"] for message in second.records) == expected_ids
    assert search.call_count == page_one.call_count == page_two.call_count == children.call_count == 2
    if sync_mode == "incremental":
        assert AirbyteMessageSerializer.dump(second.state_messages[-1])["state"]["stream"]["stream_state"]["state"] == {
            "last_edited_time": "2022-01-04T00:00:00.000000Z"
        }
