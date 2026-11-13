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


def _block(block_id: str, last_edited_time: str, has_children: bool = False) -> dict:
    return {
        "object": "block",
        "id": block_id,
        "parent": {"type": "page_id", "page_id": "page-1"},
        "created_time": "2021-01-01T00:00:00.000Z",
        "last_edited_time": last_edited_time,
        "has_children": has_children,
        "archived": False,
        "in_trash": False,
        "type": "paragraph",
        "paragraph": {"rich_text": [], "color": "default"},
    }


def _list(results: list) -> dict:
    return {"object": "list", "results": results, "next_cursor": None, "has_more": False}


def _mock_api(requests_mock, edited_blocks=()) -> None:
    requests_mock.post(
        "https://api.notion.com/v1/search",
        json=_list([{"object": "page", "id": "page-1", "last_edited_time": "2022-03-01T00:00:00.000Z"}]),
    )
    requests_mock.get(
        "https://api.notion.com/v1/blocks/page-1/children?page_size=100",
        json=_list(
            [
                _block("old-leaf", "2022-01-01T00:00:00.000Z"),
                _block("old-parent", "2022-01-02T00:00:00.000Z", has_children=True),
                _block("newest-leaf", "2022-03-01T00:00:00.000Z"),
            ]
        ),
    )
    requests_mock.get(
        "https://api.notion.com/v1/blocks/old-parent/children?page_size=100",
        json=_list([_block("old-child", "2022-01-03T00:00:00.000Z"), *edited_blocks]),
    )


def _read(state):
    source = get_source(_CONFIG, state)
    return read(source, config=_CONFIG, catalog=_CATALOG, state=state)


def _ids(output) -> list:
    return [record.record.data["id"] for record in output.records]


def _state(output) -> dict:
    return output.most_recent_state.stream_state.__dict__


def test_incremental_read_with_state_emits_only_blocks_edited_since_the_cursor(requests_mock):
    _mock_api(requests_mock)
    first = _read(StateBuilder().with_stream_state("blocks", {}).build())

    assert _ids(first) == ["old-leaf", "old-child", "old-parent", "newest-leaf"]
    assert _state(first)["state"] == {"last_edited_time": "2022-03-01T00:00:00.000000Z"}

    # A block nested under a parent that was itself not edited is the case the retriever must not lose.
    requests_mock.reset_mock()
    _mock_api(requests_mock, edited_blocks=[_block("edited-child", "2022-04-01T00:00:00.000Z")])
    second = _read(StateBuilder().with_stream_state("blocks", _state(first)).build())

    # The cursor is inclusive, so the block sitting exactly on the previous cursor value is the only repeat.
    assert _ids(second) == ["edited-child", "newest-leaf"]
    assert _state(second)["state"] == {"last_edited_time": "2022-04-01T00:00:00.000000Z"}
    assert [request.url for request in requests_mock.request_history if request.method == "GET"] == [
        "https://api.notion.com/v1/blocks/page-1/children?page_size=100",
        "https://api.notion.com/v1/blocks/old-parent/children?page_size=100",
    ]
