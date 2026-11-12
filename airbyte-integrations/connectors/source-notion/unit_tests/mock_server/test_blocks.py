# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any

import pytest
from unit_tests.conftest import get_source

from airbyte_cdk.models import AirbyteStateMessageSerializer, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


_CONFIG = {"start_date": "2024-01-01T00:00:00.000Z", "credentials": {"auth_type": "token", "token": "test-token"}, "num_workers": 1}
_OLD = "2023-12-31T00:00:00.000Z"
_START = "2024-01-01T00:00:00.000Z"
_BOUNDARY = "2024-01-02T00:00:00.000Z"
_UPDATED = "2024-01-03T00:00:00.000Z"


def _block(block_id: str, edited: str, has_children: bool = False) -> dict[str, Any]:
    return {
        "object": "block",
        "id": block_id,
        "type": "paragraph",
        "paragraph": {"rich_text": []},
        "last_edited_time": edited,
        "has_children": has_children,
        "parent": {"type": "page_id", "page_id": "page-1"},
    }


def _response(records: list[dict[str, Any]], next_cursor: str | None = None) -> dict[str, Any]:
    return {"object": "list", "results": records, "has_more": next_cursor is not None, "next_cursor": next_cursor}


@pytest.mark.parametrize(
    "ancestor_edited, initial_ids",
    [
        (_OLD, ["at-start", "boundary", "child"]),
        (_START, ["ancestor", "at-start", "boundary", "child"]),
    ],
)
def test_incremental_blocks_resume_without_reemitting_unchanged_ancestors(requests_mock, ancestor_edited, initial_ids) -> None:
    search = requests_mock.post(
        "https://api.notion.com/v1/search",
        json=_response([{"object": "page", "id": "page-1", "last_edited_time": _UPDATED, "properties": {}}]),
    )
    first_page = requests_mock.get(
        "https://api.notion.com/v1/blocks/page-1/children?page_size=100",
        complete_qs=True,
        json=_response([_block("ancestor", ancestor_edited, True), _block("at-start", _START)], "page-2"),
    )
    second_page = requests_mock.get(
        "https://api.notion.com/v1/blocks/page-1/children?page_size=100&start_cursor=page-2",
        complete_qs=True,
        json=_response([_block("boundary", _BOUNDARY)]),
    )
    initial_children = requests_mock.get(
        "https://api.notion.com/v1/blocks/ancestor/children?page_size=100",
        complete_qs=True,
        json=_response([_block("child", _BOUNDARY)]),
    )
    catalog = CatalogBuilder().with_stream("blocks", SyncMode.incremental).build()
    initial = read(get_source(_CONFIG), config=_CONFIG, catalog=catalog)
    assert sorted(record.record.data["id"] for record in initial.records) == initial_ids
    initial_state = AirbyteStateMessageSerializer.dump(initial.state_messages[-1].state)["stream"]["stream_state"]
    assert initial_state["state"] == {"last_edited_time": "2024-01-02T00:00:00.000000Z"}

    children = requests_mock.get(
        "https://api.notion.com/v1/blocks/ancestor/children?page_size=100",
        complete_qs=True,
        json=_response([_block("child", _UPDATED)]),
    )
    state = StateBuilder().with_stream_state("blocks", initial_state).build()
    resumed = read(get_source(_CONFIG, state), config=_CONFIG, catalog=catalog, state=state)
    assert sorted(record.record.data["id"] for record in resumed.records) == ["boundary", "child"]
    assert AirbyteStateMessageSerializer.dump(resumed.state_messages[-1].state)["stream"]["stream_state"]["state"] == {
        "last_edited_time": "2024-01-03T00:00:00.000000Z"
    }
    assert search.call_count == 2
    assert first_page.call_count == 2
    assert second_page.call_count == 2
    assert initial_children.call_count == 1
    assert children.call_count == 1
    assert not initial.errors
    assert not resumed.errors

    full_refresh_catalog = CatalogBuilder().with_stream("blocks", SyncMode.full_refresh).build()
    full_refresh_config = {**_CONFIG, "start_date": _OLD}
    full_refresh = read(get_source(full_refresh_config), config=full_refresh_config, catalog=full_refresh_catalog)
    assert sorted(record.record.data["id"] for record in full_refresh.records) == ["ancestor", "at-start", "boundary", "child"]
    assert not full_refresh.errors
