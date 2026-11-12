#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from unittest.mock import MagicMock, patch

import pytest

from airbyte_cdk.models import AirbyteStateMessageSerializer, ConfiguredAirbyteCatalogSerializer
from airbyte_cdk.sources.declarative.retrievers.simple_retriever import SimpleRetriever
from airbyte_cdk.sources.declarative.types import Record, StreamSlice
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


state_test_records = [
    {"id": "1", "last_edited_time": "2022-01-02T00:00:00.000Z"},
    {"id": "2", "last_edited_time": "2022-01-03T00:00:00.000Z"},
    {"id": "3", "last_edited_time": "2022-01-04T00:00:00.000Z"},
]


@pytest.mark.parametrize("sync_mode", ["incremental", "full_refresh"])
def test_blocks_incremental_state_and_descendants(requests_mock, sync_mode):
    config = {"start_date": "2020-01-01T00:00:00.000Z", "credentials": {"auth_type": "token", "token": "abcd"}}
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

    def block(identifier, edited, children=False):
        return {
            "object": "block",
            "id": identifier,
            "type": "paragraph",
            "last_edited_time": edited,
            "has_children": children,
            "parent": {"type": "page_id", "page_id": "page-1"},
        }

    def response(records):
        return {"object": "list", "results": records, "next_cursor": None, "has_more": False}

    requests_mock.post(
        "https://api.notion.com/v1/search",
        json=response([{"object": "page", "id": "page-1", "last_edited_time": "2022-01-05T00:00:00.000Z"}]),
    )
    requests_mock.get(
        "https://api.notion.com/v1/blocks/page-1/children?page_size=100", json=response([block("baseline", "2022-01-03T00:00:00.000Z")])
    )
    first = read(get_source(config), config=config, catalog=catalog)
    assert not first.errors
    assert [record.record.data["id"] for record in first.records] == ["baseline"]
    print("FIRST STATE", AirbyteStateMessageSerializer.dump(first.state_messages[-1].state))
    assert AirbyteStateMessageSerializer.dump(first.state_messages[-1].state)["stream"]["stream_state"]["state"] == {
        "last_edited_time": "2022-01-03T00:00:00.000000Z"
    }
    state = [message.state for message in first.state_messages]
    requests_mock.get(
        "https://api.notion.com/v1/blocks/page-1/children?page_size=100",
        json=response(
            [
                block("old", "2022-01-01T00:00:00.000Z"),
                block("new", "2022-01-04T00:00:00.000Z"),
                block("parent", "2022-01-02T00:00:00.000Z", True),
                dict(block("excluded", "2022-01-06T00:00:00.000Z"), type="child_page"),
            ]
        ),
    )
    child_request = requests_mock.get(
        "https://api.notion.com/v1/blocks/parent/children?page_size=100", json=response([block("child", "2022-01-05T00:00:00.000Z")])
    )
    catalog.streams[0].sync_mode = type(catalog.streams[0].sync_mode)(sync_mode)
    if sync_mode == "full_refresh":
        state = []
    output = read(get_source(config, state), config=config, catalog=catalog, state=state)
    assert not output.errors
    print("SECOND IDS", sorted(record.record.data["id"] for record in output.records))
    print("FINAL STATE", AirbyteStateMessageSerializer.dump(output.state_messages[-1].state))
    expected_ids = ["child", "new"] if sync_mode == "incremental" else ["child", "new", "old", "parent"]
    assert sorted(record.record.data["id"] for record in output.records) == expected_ids
    assert child_request.called
    if sync_mode == "incremental":
        assert AirbyteStateMessageSerializer.dump(output.state_messages[-1].state)["stream"]["stream_state"]["state"] == {
            "last_edited_time": "2022-01-05T00:00:00.000000Z"
        }
        state = [message.state for message in output.state_messages]
        for status_code in [200, 404]:
            requests_mock.get(
                "https://api.notion.com/v1/blocks/page-1/children?page_size=100",
                json=response([]),
                status_code=status_code,
            )
            empty = read(get_source(config, state), config=config, catalog=catalog, state=state)
            assert not empty.errors
            assert not empty.records
            assert AirbyteStateMessageSerializer.dump(empty.state_messages[-1].state)["stream"]["stream_state"]["state"] == {
                "last_edited_time": "2022-01-05T00:00:00.000000Z"
            }


def test_blocks_retriever_depth_restored_after_children(components_module):
    """
    Test to verify that current_block_depth is correctly incremented and decremented during recursive calls.

    This test creates a scenario with two sibling blocks at the same level, both having children:
    - Block A (has_children=True)
      - Block A1 (has_children=False)
    - Block B (has_children=True)
      - Block B1 (has_children=False)

    The depth counter should properly increment when entering a child level and decrement when
    returning to the parent level. This ensures sibling blocks are processed at the correct depth.
    """

    retriever = components_module.BlocksRetriever(
        name="test",
        primary_key=["id"],
        requester=MagicMock(),
        record_selector=MagicMock(),
        paginator=MagicMock(),
        config={},
        parameters={},
    )
    retriever._paginator = MagicMock()
    depth_tracker = []

    block_a = Record(
        data={"id": "block-a", "has_children": True}, stream_name="blocks", associated_slice=StreamSlice(partition={}, cursor_slice={})
    )
    block_a1 = Record(
        data={"id": "block-a1", "has_children": False}, stream_name="blocks", associated_slice=StreamSlice(partition={}, cursor_slice={})
    )
    block_b = Record(
        data={"id": "block-b", "has_children": True}, stream_name="blocks", associated_slice=StreamSlice(partition={}, cursor_slice={})
    )
    block_b1 = Record(
        data={"id": "block-b1", "has_children": False}, stream_name="blocks", associated_slice=StreamSlice(partition={}, cursor_slice={})
    )

    def mock_super_read_records(self, records_schema, stream_slice=None):
        depth_tracker.append(retriever.current_block_depth)

        if stream_slice is None or not stream_slice.partition:
            yield block_a
            yield block_b
        elif stream_slice.partition.get("block_id") == "block-a":
            yield block_a1
        elif stream_slice.partition.get("block_id") == "block-b":
            yield block_b1

    with patch.object(SimpleRetriever, "read_records", mock_super_read_records):
        stream_slice = StreamSlice(partition={}, cursor_slice={})
        results = list(retriever.read_records({}, stream_slice))

    assert len(depth_tracker) == 3, f"Expected 3 depth measurements, got {len(depth_tracker)}: {depth_tracker}"
    assert depth_tracker == [0, 1, 1], f"Depth should be properly managed. Depth tracker: {depth_tracker}"
    assert retriever.current_block_depth == 0, f"Final depth should be 0, got {retriever.current_block_depth}"


def test_blocks_retriever(requests_mock):
    page_response_data = {
        "object": "list",
        "results": [
            {
                "object": "page",
                "id": "page-1",
                "created_time": "2021-10-19T13:33:00.000Z",
                "last_edited_time": "2021-10-19T13:33:00.000Z",
                "created_by": {"object": "user", "id": "user-1"},
                "last_edited_by": {"object": "user", "id": "fuser-1"},
                "cover": None,
                "icon": None,
                "parent": {"type": "database_id", "database_id": "database-id"},
                "archived": False,
                "in_trash": False,
                "properties": {
                    "Name": {
                        "id": "title",
                        "type": "title",
                        "title": [
                            {
                                "type": "text",
                                "text": {"content": "Test Data 1", "link": None},
                                "annotations": {
                                    "bold": False,
                                    "italic": False,
                                    "strikethrough": False,
                                    "underline": False,
                                    "code": False,
                                    "color": "default",
                                },
                                "plain_text": "Test Data 1",
                                "href": None,
                            }
                        ],
                    }
                },
                "url": "https://www.notion.so/url-1",
                "public_url": None,
            }
        ],
        "next_cursor": None,
        "has_more": False,
        "type": "page_or_database",
        "page_or_database": {},
        "request_id": "request-1",
    }
    requests_mock.register_uri(
        "POST",
        "https://api.notion.com/v1/search",
        [{"json": page_response_data}],
    )

    page_blocks_response_data = {
        "object": "list",
        "results": [
            {
                "object": "block",
                "id": "block-id-1",
                "parent": {"type": "page_id", "page_id": "page-1"},
                "created_time": "2021-10-19T13:33:00.000Z",
                "last_edited_time": "2021-10-19T13:33:00.000Z",
                "created_by": {"object": "user", "id": "user-1"},
                "last_edited_by": {"object": "user", "id": "user-1"},
                "has_children": False,
                "archived": False,
                "in_trash": False,
                "type": "callout",
                "callout": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": "Notion Tip: ", "link": None},
                            "annotations": {
                                "bold": True,
                                "italic": False,
                                "strikethrough": False,
                                "underline": False,
                                "code": False,
                                "color": "default",
                            },
                            "plain_text": "Notion Tip: ",
                            "href": None,
                        }
                    ],
                    "icon": {"type": "emoji", "emoji": "💡"},
                    "color": "gray_background",
                },
            },
            {
                "object": "block",
                "id": "block-id-2",
                "parent": {"type": "page_id", "page_id": "page-1"},
                "created_time": "2021-10-19T13:33:00.000Z",
                "last_edited_time": "2021-11-19T13:33:00.000Z",
                "created_by": {"object": "user", "id": "user-1"},
                "last_edited_by": {"object": "user", "id": "user-1"},
                "has_children": True,
                "archived": False,
                "in_trash": False,
                "type": "callout",
                "callout": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": "Notion Tip: ", "link": None},
                            "annotations": {
                                "bold": True,
                                "italic": False,
                                "strikethrough": False,
                                "underline": False,
                                "code": False,
                                "color": "default",
                            },
                            "plain_text": "Notion Tip: ",
                            "href": None,
                        }
                    ],
                    "icon": {"type": "emoji", "emoji": "💡"},
                    "color": "gray_background",
                },
            },
        ],
        "next_cursor": None,
        "has_more": False,
        "type": "block",
        "block": {},
        "request_id": "request-id-2",
    }
    requests_mock.register_uri(
        "GET",
        "https://api.notion.com/v1/blocks/page-1/children?page_size=100",
        [{"json": page_blocks_response_data}],
    )

    block_children_response_data = {
        "object": "list",
        "results": [
            {
                "object": "block",
                "id": "block-id-3",
                "parent": {"type": "page_id", "page_id": "page-1"},
                "created_time": "2021-10-19T13:33:00.000Z",
                "last_edited_time": "2021-11-19T13:33:00.000Z",
                "created_by": {"object": "user", "id": "user-1"},
                "last_edited_by": {"object": "user", "id": "user-1"},
                "has_children": False,
                "archived": False,
                "in_trash": False,
                "type": "callout",
                "callout": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": "Notion Tip: ", "link": None},
                            "annotations": {
                                "bold": True,
                                "italic": False,
                                "strikethrough": False,
                                "underline": False,
                                "code": False,
                                "color": "default",
                            },
                            "plain_text": "Notion Tip: ",
                            "href": None,
                        }
                    ],
                    "icon": {"type": "emoji", "emoji": "💡"},
                    "color": "gray_background",
                },
            }
        ],
        "next_cursor": None,
        "has_more": False,
        "type": "block",
        "block": {},
        "request_id": "request-id-2",
    }
    requests_mock.register_uri(
        "GET",
        "https://api.notion.com/v1/blocks/block-id-2/children?page_size=100",
        [{"json": block_children_response_data}],
    )

    config_mock = {"start_date": "2020-01-01T00:00:00.000Z", "credentials": {"auth_type": "token", "token": "abcd"}}
    blocks_stream_name = "blocks"
    catalog = ConfiguredAirbyteCatalogSerializer.load(
        {
            "streams": [
                {
                    "stream": {"name": blocks_stream_name, "json_schema": {}, "supported_sync_modes": ["full_refresh", "incremental"]},
                    "sync_mode": "incremental",
                    "destination_sync_mode": "append",
                }
            ]
        }
    )
    state = StateBuilder().with_stream_state(blocks_stream_name, {}).build()
    source = get_source(config_mock, state)
    output = read(source, config=config_mock, catalog=catalog, state=state)
    assert len(output.records) == 3
