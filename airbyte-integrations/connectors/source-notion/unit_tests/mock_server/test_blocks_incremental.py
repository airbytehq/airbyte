# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
from unit_tests.conftest import get_source

from airbyte_cdk.models import ConfiguredAirbyteCatalogSerializer
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


@pytest.mark.parametrize(
    "stream_state",
    [
        {"last_edited_time": "2024-06-01T00:00:00.000Z"},
        {"state": {"last_edited_time": "2024-06-01T00:00:00.000Z"}, "use_global_cursor": True},
        None,
    ],
    ids=["legacy-flat-state", "global-substream-state", "full-refresh-no-state"],
)
def test_blocks_incremental_filters_old_blocks(requests_mock, stream_state):
    config = {"start_date": "2020-01-01T00:00:00.000Z", "credentials": {"auth_type": "token", "token": "abcd"}}
    old = "2024-05-01T00:00:00.000Z"
    new = "2024-07-01T00:00:00.000Z"
    newest = "2024-08-01T00:00:00.000Z"
    sync_mode = "full_refresh" if stream_state is None else "incremental"
    state = StateBuilder().build() if stream_state is None else StateBuilder().with_stream_state("blocks", stream_state).build()
    requests_mock.post(
        "https://api.notion.com/v1/search",
        json={
            "results": [
                {"object": "page", "id": "old-page", "last_edited_time": old},
                {"object": "page", "id": "new-page", "last_edited_time": new},
            ],
            "has_more": False,
            "next_cursor": None,
        },
    )
    for page in ["old-page", "new-page"]:
        requests_mock.get(
            f"https://api.notion.com/v1/blocks/{page}/children",
            json={
                "results": [
                    {
                        "id": f"{page}-old",
                        "type": "paragraph",
                        "has_children": True,
                        "last_edited_time": old,
                        "parent": {"type": "page_id", "page_id": page},
                    },
                    {
                        "id": f"{page}-new",
                        "type": "paragraph",
                        "has_children": False,
                        "last_edited_time": new,
                        "parent": {"type": "page_id", "page_id": page},
                    },
                ],
                "has_more": False,
                "next_cursor": None,
            },
        )
        requests_mock.get(
            f"https://api.notion.com/v1/blocks/{page}-old/children",
            json={
                "results": [
                    {"id": f"{page}-nested-old", "type": "paragraph", "has_children": False, "last_edited_time": old},
                    {"id": f"{page}-nested-new", "type": "paragraph", "has_children": False, "last_edited_time": newest},
                ],
                "has_more": False,
                "next_cursor": None,
            },
        )
    catalog = ConfiguredAirbyteCatalogSerializer.load(
        {
            "streams": [
                {
                    "stream": {"name": "blocks", "json_schema": {}, "supported_sync_modes": ["incremental", "full_refresh"]},
                    "sync_mode": sync_mode,
                    "destination_sync_mode": "append",
                }
            ]
        }
    )
    output = read(get_source(config, state), config=config, catalog=catalog, state=state)
    assert sorted((request.method, request.path_url) for request in requests_mock.request_history) == [
        ("GET", "/v1/blocks/new-page-old/children?page_size=100"),
        ("GET", "/v1/blocks/new-page/children?page_size=100"),
        ("GET", "/v1/blocks/old-page-old/children?page_size=100"),
        ("GET", "/v1/blocks/old-page/children?page_size=100"),
        ("POST", "/v1/search"),
    ]
    emitted_ids = sorted(message.record.data["id"] for message in output.records)
    for message in output.records:
        if message.record.data["id"].endswith("-new") and "parent" in message.record.data:
            assert message.record.data["parent"]["sequence_number"] == 1
    if sync_mode == "full_refresh":
        assert emitted_ids == sorted(
            f"{page}-{suffix}" for page in ["old-page", "new-page"] for suffix in ["old", "new", "nested-old", "nested-new"]
        )
        return
    final_state = vars(output.state_messages[-1].state.stream.stream_state)
    for page in ["old-page", "new-page"]:
        requests_mock.get(
            f"https://api.notion.com/v1/blocks/{page}-old/children",
            json={
                "results": [
                    {"id": f"{page}-nested-old", "type": "paragraph", "has_children": False, "last_edited_time": old},
                    {
                        "id": f"{page}-second-new",
                        "type": "paragraph",
                        "has_children": False,
                        "last_edited_time": "2024-09-01T00:00:00.000Z",
                    },
                ],
                "has_more": False,
                "next_cursor": None,
            },
        )
    next_state = StateBuilder().with_stream_state("blocks", final_state).build()
    second_output = read(get_source(config, next_state), config=config, catalog=catalog, state=next_state)
    second_records = [message.record.data for message in second_output.records]
    observed = {
        "first_ids": emitted_ids,
        "state_value": final_state.get("state"),
        "state_keys": sorted(final_state),
        "global_cursor": final_state.get("use_global_cursor"),
        "second_ids": sorted(record["id"] for record in second_records),
        "second_read_has_older_records": any(record["last_edited_time"] < newest for record in second_records),
    }
    assert observed == {
        "first_ids": ["new-page-nested-new", "new-page-new", "old-page-nested-new", "old-page-new"],
        "state_value": {"last_edited_time": "2024-08-01T00:00:00.000000Z"},
        "state_keys": ["lookback_window", "parent_state", "state", "use_global_cursor"],
        "global_cursor": True,
        "second_ids": ["new-page-second-new", "old-page-second-new"],
        "second_read_has_older_records": False,
    }
