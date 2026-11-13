# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any, Dict, List, Mapping

import pytest

from airbyte_cdk.models import ConfiguredAirbyteCatalogSerializer
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


_CONFIG = {"start_date": "2020-01-01T00:00:00.000Z", "credentials": {"auth_type": "token", "token": "abcd"}}
_URL_BASE = "https://api.notion.com/v1"
_STATE_VALUE = "2023-06-01T00:00:00.000Z"
_OLD = "2023-01-01T00:00:00.000Z"
_NEW = "2023-07-01T00:00:00.000Z"


def _list_response(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {"object": "list", "results": results, "next_cursor": None, "has_more": False}


def _block(block_id: str, last_edited_time: str, has_children: bool = False) -> Dict[str, Any]:
    return {
        "object": "block",
        "id": block_id,
        "type": "paragraph",
        "parent": {"type": "page_id", "page_id": "page-1"},
        "last_edited_time": last_edited_time,
        "has_children": has_children,
    }


def _incremental_catalog():
    return ConfiguredAirbyteCatalogSerializer.load(
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


@pytest.mark.parametrize(
    "stream_state",
    [
        pytest.param({"last_edited_time": _STATE_VALUE}, id="legacy_flat_state"),
        pytest.param(
            {"use_global_cursor": True, "state": {"last_edited_time": _STATE_VALUE}, "lookback_window": 1, "parent_state": {}},
            id="global_substream_cursor_state",
        ),
    ],
)
def test_incremental_read_emits_only_blocks_edited_after_state(requests_mock, stream_state: Mapping[str, Any]):
    requests_mock.post(
        f"{_URL_BASE}/search",
        json=_list_response([{"object": "page", "id": "page-1", "last_edited_time": _NEW, "properties": {}}]),
    )
    requests_mock.get(
        f"{_URL_BASE}/blocks/page-1/children",
        json=_list_response([_block("old-parent", _OLD, has_children=True), _block("old-sibling", _OLD), _block("new-sibling", _NEW)]),
    )
    requests_mock.get(
        f"{_URL_BASE}/blocks/old-parent/children",
        json=_list_response([_block("old-child", _OLD), _block("new-child", _NEW)]),
    )
    state = StateBuilder().with_stream_state("blocks", stream_state).build()

    output = read(get_source(_CONFIG, state), config=_CONFIG, catalog=_incremental_catalog(), state=state)

    assert [record.record.data["id"] for record in output.records] == ["new-child", "new-sibling"]
    assert [request.path for request in requests_mock.request_history if request.method == "GET"] == [
        "/v1/blocks/page-1/children",
        "/v1/blocks/old-parent/children",
    ]
    assert output.most_recent_state.stream_state.state == {"last_edited_time": "2023-07-01T00:00:00.000000Z"}
