# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from airbyte_cdk.models import ConfiguredAirbyteCatalogSerializer
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


_CONFIG = {"start_date": "2020-01-01T00:00:00.000Z", "credentials": {"auth_type": "token", "token": "abcd"}}
_CATALOG = ConfiguredAirbyteCatalogSerializer.load(
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
_PAGE_BLOCKS_URL = "https://api.notion.com/v1/blocks/page-1/children?page_size=100"
_NESTED_BLOCKS_URL = "https://api.notion.com/v1/blocks/block-2/children?page_size=100"


def _block(block_id: str, last_edited_time: str, has_children: bool = False) -> dict:
    return {
        "object": "block",
        "id": block_id,
        "parent": {"type": "page_id", "page_id": "page-1"},
        "created_time": "2021-10-19T13:33:00.000Z",
        "last_edited_time": last_edited_time,
        "has_children": has_children,
        "archived": False,
        "in_trash": False,
        "type": "paragraph",
        "paragraph": {"rich_text": [], "color": "default"},
    }


def _list(results: list) -> dict:
    return {"object": "list", "results": results, "next_cursor": None, "has_more": False}


def _read_blocks(requests_mock, state, page_blocks: list, nested_blocks: list):
    requests_mock.post(
        "https://api.notion.com/v1/search",
        json=_list([{"object": "page", "id": "page-1", "last_edited_time": "2021-12-01T10:00:00.000Z", "properties": {}}]),
    )
    requests_mock.get(_PAGE_BLOCKS_URL, json=_list(page_blocks))
    requests_mock.get(_NESTED_BLOCKS_URL, json=_list(nested_blocks))
    output = read(get_source(_CONFIG, state), config=_CONFIG, catalog=_CATALOG, state=state)
    assert output.errors == []
    return output


def test_blocks_second_incremental_read_emits_only_blocks_edited_since_state(requests_mock):
    first = _read_blocks(
        requests_mock,
        StateBuilder().with_stream_state("blocks", {}).build(),
        page_blocks=[_block("block-1", "2021-10-19T13:33:00.000Z"), _block("block-2", "2021-11-19T13:33:00.000Z", has_children=True)],
        nested_blocks=[_block("block-3", "2021-11-01T13:33:00.000Z")],
    )
    assert [record.record.data["id"] for record in first.records] == ["block-1", "block-3", "block-2"]
    first_state = first.most_recent_state.stream_state.__dict__
    assert first_state["state"] == {"last_edited_time": "2021-11-19T13:33:00.000000Z"}

    # Since the first read: block-2 was edited and gained the nested block-4, block-5 was added with the same
    # timestamp as the saved state, and block-1 and block-3 are untouched.
    requests_mock.reset_mock()
    second = _read_blocks(
        requests_mock,
        StateBuilder().with_stream_state("blocks", first_state).build(),
        page_blocks=[
            _block("block-1", "2021-10-19T13:33:00.000Z"),
            _block("block-2", "2021-12-01T10:00:00.000Z", has_children=True),
            _block("block-5", "2021-11-19T13:33:00.000Z"),
        ],
        nested_blocks=[_block("block-3", "2021-11-01T13:33:00.000Z"), _block("block-4", "2021-12-01T10:00:00.000Z")],
    )

    # The cursor is inclusive, so block-5 (equal to the saved state) is read again; the untouched blocks are not.
    assert [record.record.data["id"] for record in second.records] == ["block-4", "block-2", "block-5"]
    assert second.most_recent_state.stream_state.__dict__["state"] == {"last_edited_time": "2021-12-01T10:00:00.000000Z"}
    # Filtering is client-side: the page and the edited parent block are still requested from Notion.
    get_urls = [request.url for request in requests_mock.request_history if request.method == "GET"]
    assert get_urls == [_PAGE_BLOCKS_URL, _NESTED_BLOCKS_URL]
