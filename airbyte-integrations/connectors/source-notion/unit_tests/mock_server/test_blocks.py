# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any, Dict, List, Optional

import pytest
from freezegun import freeze_time

from airbyte_cdk.models import ConfiguredAirbyteCatalogSerializer
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


_API = "https://api.notion.com/v1"
_OLD = "2021-10-19T13:33:00.000Z"
_NEW = "2021-12-01T00:00:00.000Z"
_STREAM = "blocks"


def _block(block_id: str, last_edited_time: str, parent_id: str, has_children: bool = False) -> Dict[str, Any]:
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
        "paragraph": {"rich_text": []},
    }


def _list(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {"object": "list", "results": results, "next_cursor": None, "has_more": False}


def _catalog(sync_mode: str):
    return ConfiguredAirbyteCatalogSerializer.load(
        {
            "streams": [
                {
                    "stream": {"name": _STREAM, "json_schema": {}, "supported_sync_modes": ["full_refresh", "incremental"]},
                    "sync_mode": sync_mode,
                    "destination_sync_mode": "append",
                }
            ]
        }
    )


def _mock_page_with_nested_blocks(requests_mock) -> None:
    """
    page-1
      - old-parent (edited before the cursor, has children)
          - old-child (edited before the cursor)
          - new-child (edited after the cursor)
      - new-block (edited after the cursor)
    """
    requests_mock.post(f"{_API}/search", json=_list([{"object": "page", "id": "page-1", "last_edited_time": _NEW, "properties": {}}]))
    requests_mock.get(
        f"{_API}/blocks/page-1/children",
        json=_list([_block("old-parent", _OLD, "page-1", has_children=True), _block("new-block", _NEW, "page-1")]),
    )
    requests_mock.get(
        f"{_API}/blocks/old-parent/children",
        json=_list([_block("old-child", _OLD, "old-parent"), _block("new-child", _NEW, "old-parent")]),
    )


_ALL_BLOCKS = ["old-child", "new-child", "old-parent", "new-block"]
_EDITED_SINCE_STATE = ["new-child", "new-block"]


@pytest.mark.parametrize(
    "sync_mode,start_date,stream_state,expected_ids",
    [
        pytest.param(
            "incremental",
            "2020-01-01T00:00:00.000Z",
            {"last_edited_time": "2021-11-01T00:00:00.000Z"},
            _EDITED_SINCE_STATE,
            id="incremental_legacy_state_skips_blocks_edited_before_state",
        ),
        pytest.param(
            "incremental",
            "2020-01-01T00:00:00.000Z",
            {"use_global_cursor": True, "state": {"last_edited_time": "2021-11-01T00:00:00.000Z"}, "lookback_window": 0},
            _EDITED_SINCE_STATE,
            id="incremental_global_state_skips_blocks_edited_before_state",
        ),
        pytest.param(
            "incremental",
            None,
            {"use_global_cursor": True, "state": {"last_edited_time": "2021-11-01T00:00:00.000Z"}, "lookback_window": 0},
            _EDITED_SINCE_STATE,
            id="incremental_state_without_configured_start_date_skips_blocks_edited_before_state",
        ),
        pytest.param(
            "incremental",
            "2020-01-01T00:00:00.000Z",
            {"last_edited_time": "2021-01-01T00:00:00.000Z"},
            _ALL_BLOCKS,
            id="incremental_state_before_all_edits_emits_every_block",
        ),
        pytest.param(
            "incremental",
            "2021-11-01T00:00:00.000Z",
            None,
            _ALL_BLOCKS,
            id="incremental_first_sync_emits_every_block",
        ),
        pytest.param(
            "full_refresh",
            "2021-11-01T00:00:00.000Z",
            None,
            _ALL_BLOCKS,
            id="full_refresh_emits_every_block",
        ),
    ],
)
@freeze_time("2022-06-01T00:00:00Z")  # default start date (730 days back) is 2020-06-01, before every fixture
def test_read_emits_only_blocks_edited_since_state(
    requests_mock, sync_mode: str, start_date: Optional[str], stream_state: Optional[Dict[str, Any]], expected_ids: List[str]
) -> None:
    _mock_page_with_nested_blocks(requests_mock)
    config = {"credentials": {"auth_type": "token", "token": "abcd"}}
    if start_date:
        config["start_date"] = start_date
    state = StateBuilder().with_stream_state(_STREAM, stream_state).build() if stream_state else StateBuilder().build()

    output = read(get_source(config, state), config=config, catalog=_catalog(sync_mode), state=state)

    assert [record.record.data["id"] for record in output.records] == expected_ids
    # children of an unchanged parent block are still fetched, so edited nested blocks are not lost
    requested_paths = [request.path for request in requests_mock.request_history if request.method == "GET"]
    assert requested_paths == ["/v1/blocks/page-1/children", "/v1/blocks/old-parent/children"]
    if sync_mode == "incremental":
        assert output.most_recent_state.stream_state.state == {"last_edited_time": "2021-12-01T00:00:00.000000Z"}
