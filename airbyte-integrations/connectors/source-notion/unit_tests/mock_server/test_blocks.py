# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any, Dict, List

from airbyte_cdk.models import AirbyteStateMessage, ConfiguredAirbyteCatalogSerializer
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from unit_tests.conftest import get_source


_CONFIG = {"start_date": "2020-01-01T00:00:00.000Z", "credentials": {"auth_type": "token", "token": "test-token"}}
_FIRST_SYNC_TIME = "2025-06-01T00:00:00.000Z"
_SECOND_SYNC_TIME = "2025-07-01T00:00:00.000Z"
_OLD_TIME = "2021-01-01T00:00:00.000Z"


def _page(page_id: str, last_edited_time: str) -> Dict[str, Any]:
    return {"object": "page", "id": page_id, "last_edited_time": last_edited_time, "properties": {}}


def _block(block_id: str, page_id: str, last_edited_time: str) -> Dict[str, Any]:
    return {
        "object": "block",
        "id": block_id,
        "parent": {"type": "page_id", "page_id": page_id},
        "created_time": _OLD_TIME,
        "last_edited_time": last_edited_time,
        "has_children": False,
        "type": "paragraph",
        "paragraph": {},
    }


def _list(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {"object": "list", "results": results, "has_more": False, "next_cursor": None}


def _read_blocks(requests_mock, edited_page_time: str, edited_block_time: str, state: List[AirbyteStateMessage]) -> EntrypointOutput:
    requests_mock.post(
        "https://api.notion.com/v1/search",
        json=_list([_page("edited-page", edited_page_time), _page("unchanged-page", _OLD_TIME)]),
    )
    requests_mock.get(
        "https://api.notion.com/v1/blocks/edited-page/children",
        json=_list([_block("edited-block", "edited-page", edited_block_time), _block("old-block", "edited-page", _OLD_TIME)]),
    )
    requests_mock.get(
        "https://api.notion.com/v1/blocks/unchanged-page/children",
        json=_list([_block("unchanged-block", "unchanged-page", _OLD_TIME)]),
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
    return read(get_source(_CONFIG, state), config=_CONFIG, catalog=catalog, state=state)


def _requested_block_paths(requests_mock) -> List[str]:
    return [request.path for request in requests_mock.request_history if request.method == "GET"]


def test_incremental_blocks_read_only_requests_children_of_pages_edited_since_last_sync(requests_mock):
    first_sync = _read_blocks(requests_mock, _FIRST_SYNC_TIME, _FIRST_SYNC_TIME, state=[])
    assert sorted(record.record.data["id"] for record in first_sync.records) == ["edited-block", "old-block", "unchanged-block"]
    first_sync_state = first_sync.state_messages[-1].state

    requests_mock.reset_mock()
    second_sync = _read_blocks(requests_mock, _SECOND_SYNC_TIME, _SECOND_SYNC_TIME, state=[first_sync_state])

    assert _requested_block_paths(requests_mock) == ["/v1/blocks/edited-page/children"]
    assert [record.record.data["id"] for record in second_sync.records] == ["edited-block"]
    second_sync_state = second_sync.state_messages[-1].state.stream.stream_state
    assert second_sync_state.state == {"last_edited_time": "2025-07-01T00:00:00.000000Z"}
    assert second_sync_state.parent_state == {"pages": {"last_edited_time": "2025-07-01T00:00:00.000000Z"}}
