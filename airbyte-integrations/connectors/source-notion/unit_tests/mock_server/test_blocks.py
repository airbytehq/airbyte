# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


_CONFIG = {"credentials": {"auth_type": "token", "token": "test-token"}, "start_date": "2020-01-01T00:00:00.000Z"}
_API = "https://api.notion.com/v1"


def _block(block_id, last_edited_time, has_children=False):
    return {
        "object": "block",
        "id": block_id,
        "type": "paragraph",
        "has_children": has_children,
        "last_edited_time": last_edited_time,
        "parent": {"type": "page_id", "page_id": "page-1"},
        "paragraph": {},
    }


def _list(results):
    return {"object": "list", "results": results, "has_more": False, "next_cursor": None}


@pytest.mark.parametrize(
    "state,expected_ids",
    [
        pytest.param(None, ["old-child", "old-parent", "new-block"], id="first_sync_emits_all_blocks"),
        pytest.param(
            {"last_edited_time": "2024-01-01T00:00:00.000Z"},
            ["new-block"],
            id="incremental_sync_emits_only_blocks_edited_since_state",
        ),
    ],
)
def test_blocks_incremental_read_filters_on_last_edited_time(requests_mock, state, expected_ids):
    requests_mock.post(
        f"{_API}/search",
        json=_list(
            [
                {
                    "object": "page",
                    "id": "page-1",
                    "last_edited_time": "2024-06-01T00:00:00.000Z",
                    "parent": {"type": "workspace"},
                    "properties": {},
                }
            ]
        ),
    )
    requests_mock.get(
        f"{_API}/blocks/page-1/children",
        json=_list([_block("old-parent", "2023-01-01T00:00:00.000Z", has_children=True), _block("new-block", "2024-05-01T00:00:00.000Z")]),
    )
    requests_mock.get(
        f"{_API}/blocks/old-parent/children",
        json=_list([_block("old-child", "2022-01-01T00:00:00.000Z")]),
    )
    catalog = CatalogBuilder().with_stream("blocks", SyncMode.incremental).build()
    state_messages = StateBuilder().with_stream_state("blocks", state).build() if state else None

    output = read(get_source(_CONFIG, state_messages), _CONFIG, catalog, state_messages)

    assert [message.record.data["id"] for message in output.records] == expected_ids
    assert output.most_recent_state.stream_state.state == {"last_edited_time": "2024-05-01T00:00:00.000000Z"}
