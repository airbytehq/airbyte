#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from unittest.mock import MagicMock, patch

from airbyte_cdk.models import ConfiguredAirbyteCatalogSerializer
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


def _block(block_id, last_edited_time, has_children=False):
    return {
        "object": "block",
        "id": block_id,
        "parent": {"type": "page_id", "page_id": "page-1"},
        "last_edited_time": last_edited_time,
        "has_children": has_children,
        "type": "paragraph",
    }


def _list_response(results):
    return {"object": "list", "results": results, "next_cursor": None, "has_more": False}


def _read_blocks_incremental(requests_mock, page_blocks, nested_blocks, stream_state):
    """Read `blocks` for one page whose block `parent` holds `nested_blocks`; returns the output and the requests sent."""
    requests_mock.reset_mock()
    requests_mock.post(
        "https://api.notion.com/v1/search",
        json=_list_response([{"object": "page", "id": "page-1", "last_edited_time": "2023-08-02T00:00:00.000Z"}]),
    )
    requests_mock.get("https://api.notion.com/v1/blocks/page-1/children?page_size=100", json=_list_response(page_blocks))
    requests_mock.get("https://api.notion.com/v1/blocks/parent/children?page_size=100", json=_list_response(nested_blocks))

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
    state = StateBuilder().with_stream_state("blocks", stream_state).build()
    output = read(get_source(config, state), config=config, catalog=catalog, state=state)
    assert output.errors == []
    return output, [f"{request.method} {request.url}" for request in requests_mock.request_history]


def test_blocks_incremental_read_emits_only_blocks_edited_since_the_state(requests_mock):
    """
    A second incremental read emits only the blocks edited at or after the saved cursor value. Blocks under a parent
    that was not edited itself are still fetched, so their edits are not lost.
    """
    first_output, _ = _read_blocks_incremental(
        requests_mock,
        page_blocks=[
            _block("old", "2023-01-01T00:00:00.000Z"),
            _block("parent", "2023-02-01T00:00:00.000Z", has_children=True),
            _block("latest", "2023-07-02T00:00:00.000Z"),
        ],
        nested_blocks=[_block("nested-old", "2023-01-05T00:00:00.000Z"), _block("nested-edited-later", "2023-01-06T00:00:00.000Z")],
        stream_state={},
    )
    assert [record.record.data["id"] for record in first_output.records] == ["old", "nested-old", "nested-edited-later", "parent", "latest"]
    first_state = first_output.most_recent_state.stream_state.__dict__
    assert first_state["state"] == {"last_edited_time": "2023-07-02T00:00:00.000000Z"}

    # Between the two syncs one nested block is edited and one block is added; `parent` itself is left untouched.
    second_output, second_requests = _read_blocks_incremental(
        requests_mock,
        page_blocks=[
            _block("old", "2023-01-01T00:00:00.000Z"),
            _block("parent", "2023-02-01T00:00:00.000Z", has_children=True),
            _block("latest", "2023-07-02T00:00:00.000Z"),
            _block("added", "2023-08-02T00:00:00.000Z"),
        ],
        nested_blocks=[_block("nested-old", "2023-01-05T00:00:00.000Z"), _block("nested-edited-later", "2023-08-01T00:00:00.000Z")],
        stream_state=first_state,
    )

    # `latest` sits exactly on the saved cursor value: the lower bound is inclusive, so it is the one expected repeat.
    assert [record.record.data["id"] for record in second_output.records] == ["nested-edited-later", "latest", "added"]
    # The position among the siblings counts the blocks that are filtered out too.
    assert [record.record.data["parent"]["sequence_number"] for record in second_output.records] == [1, 2, 3]
    assert second_requests == [
        "POST https://api.notion.com/v1/search",
        "GET https://api.notion.com/v1/blocks/page-1/children?page_size=100",
        "GET https://api.notion.com/v1/blocks/parent/children?page_size=100",
    ]
    assert second_output.most_recent_state.stream_state.__dict__["state"] == {"last_edited_time": "2023-08-02T00:00:00.000000Z"}
