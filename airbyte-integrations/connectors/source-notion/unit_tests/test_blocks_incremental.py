# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any, Dict, List, Mapping, Optional

from airbyte_cdk.models import ConfiguredAirbyteCatalogSerializer
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


_CONFIG = {"start_date": "2020-01-01T00:00:00.000Z", "credentials": {"auth_type": "token", "token": "abcd"}}
_STREAM = "blocks"
_API = "https://api.notion.com/v1"


def _block(block_id: str, parent_id: str, last_edited_time: str, has_children: bool = False) -> Dict[str, Any]:
    return {
        "object": "block",
        "id": block_id,
        "parent": {"type": "page_id", "page_id": parent_id},
        "created_time": "2021-01-01T00:00:00.000Z",
        "last_edited_time": last_edited_time,
        "has_children": has_children,
        "archived": False,
        "in_trash": False,
        "type": "paragraph",
        "paragraph": {"rich_text": [], "color": "default"},
    }


def _list(results: List[Mapping[str, Any]]) -> Dict[str, Any]:
    return {"object": "list", "results": results, "next_cursor": None, "has_more": False}


def _mock_workspace(requests_mock, child_edited_time: str) -> None:
    page = {"object": "page", "id": "page-1", "last_edited_time": "2024-06-01T00:00:00.000Z", "properties": {}}
    requests_mock.post(f"{_API}/search", json=_list([page]))
    requests_mock.get(
        f"{_API}/blocks/page-1/children?page_size=100",
        json=_list(
            [
                _block("unchanged-parent", "page-1", "2023-01-01T00:00:00.000Z", has_children=True),
                _block("unchanged", "page-1", "2023-01-01T00:00:00.000Z"),
                _block("edited", "page-1", "2024-06-01T00:00:00.000Z"),
            ]
        ),
    )
    requests_mock.get(
        f"{_API}/blocks/unchanged-parent/children?page_size=100",
        json=_list([_block("nested-child", "unchanged-parent", child_edited_time)]),
    )


def _read(state: Optional[Mapping[str, Any]]) -> EntrypointOutput:
    catalog = ConfiguredAirbyteCatalogSerializer.load(
        {
            "streams": [
                {
                    "stream": {"name": _STREAM, "json_schema": {}, "supported_sync_modes": ["full_refresh", "incremental"]},
                    "sync_mode": "incremental",
                    "destination_sync_mode": "append",
                }
            ]
        }
    )
    state_messages = StateBuilder().with_stream_state(_STREAM, state or {}).build()
    return read(get_source(_CONFIG, state_messages), config=_CONFIG, catalog=catalog, state=state_messages)


def _record_ids(output: EntrypointOutput) -> List[str]:
    return [message.record.data["id"] for message in output.records]


def _cursor_value(output: EntrypointOutput) -> str:
    return output.most_recent_state.stream_state.__dict__["state"]["last_edited_time"]


def test_incremental_read_only_emits_blocks_edited_since_saved_state(requests_mock):
    _mock_workspace(requests_mock, child_edited_time="2023-01-01T00:00:00.000Z")
    first = _read(state=None)
    assert _record_ids(first) == ["nested-child", "unchanged-parent", "unchanged", "edited"]
    saved_state = first.most_recent_state.stream_state.__dict__
    assert _cursor_value(first).startswith("2024-06-01T00:00:00")

    requests_mock.reset_mock()
    _mock_workspace(requests_mock, child_edited_time="2024-07-01T00:00:00.000Z")
    second = _read(state=saved_state)

    # Blocks not edited since the saved cursor are skipped, but the children of an unchanged
    # block are still fetched so an edited nested block is not missed. "edited" sits exactly on
    # the saved cursor and is re-emitted as the documented inclusive overlap.
    assert _record_ids(second) == ["nested-child", "edited"]
    assert [request.path for request in requests_mock.request_history] == [
        "/v1/search",
        "/v1/blocks/page-1/children",
        "/v1/blocks/unchanged-parent/children",
    ]
    assert _cursor_value(second).startswith("2024-07-01T00:00:00")
