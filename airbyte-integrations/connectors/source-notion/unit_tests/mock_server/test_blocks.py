# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from collections import Counter
from typing import Any

import pytest
from freezegun import freeze_time
from requests_mock import Mocker

from airbyte_cdk.models import AirbyteStateMessage, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


CONFIG = {"start_date": "2024-01-01T00:00:00.000Z", "credentials": {"auth_type": "token", "token": "abcd"}}


def _block(block_id: str, edited: str, parent_id: str, has_children: bool = False) -> dict[str, Any]:
    return {
        "object": "block",
        "id": block_id,
        "type": "paragraph",
        "paragraph": {"rich_text": []},
        "parent": {"type": "block_id", "block_id": parent_id},
        "has_children": has_children,
        "last_edited_time": edited,
    }


def _response(records: list[dict[str, Any]], next_cursor: str | None = None) -> dict[str, Any]:
    return {"object": "list", "results": records, "has_more": next_cursor is not None, "next_cursor": next_cursor}


def _mock_blocks(requests_mock: Mocker, child_edited: str, add_new_block: bool = False) -> None:
    requests_mock.post(
        "https://api.notion.com/v1/search",
        json=_response(
            [
                {"object": "page", "id": page_id, "last_edited_time": "2024-01-06T00:00:00.000Z", "properties": {}}
                for page_id in ["page-1", "page-2"]
            ]
        ),
    )
    requests_mock.get(
        "https://api.notion.com/v1/blocks/page-1/children?page_size=100",
        complete_qs=True,
        json=_response([_block("old-parent", "2024-01-01T00:00:00.000Z", "page-1", True)], "page-token"),
    )
    requests_mock.get(
        "https://api.notion.com/v1/blocks/page-1/children?page_size=100&start_cursor=page-token",
        complete_qs=True,
        json=_response([_block("boundary", "2024-01-03T00:00:00.000Z", "page-1")]),
    )
    requests_mock.get(
        "https://api.notion.com/v1/blocks/old-parent/children?page_size=100",
        complete_qs=True,
        json=_response([_block("nested-child", child_edited, "old-parent")]),
    )
    second_page_blocks = [_block("old-sibling", "2024-01-01T00:00:00.000Z", "page-2")]
    if add_new_block:
        second_page_blocks.append(_block("new-block", "2024-01-05T00:00:00.000Z", "page-2"))
    requests_mock.get(
        "https://api.notion.com/v1/blocks/page-2/children?page_size=100",
        complete_qs=True,
        json=_response(second_page_blocks),
    )


def _read_blocks(
    requests_mock: Mocker, config: dict[str, Any], state: list[AirbyteStateMessage], sync_mode: SyncMode = SyncMode.incremental
) -> EntrypointOutput:
    requests_mock.reset_mock()
    catalog = CatalogBuilder().with_stream("blocks", sync_mode).build()
    output = read(get_source(config, state), config, catalog, state=state)
    assert not output.errors
    assert Counter(request.path for request in requests_mock.request_history) == Counter(
        {"/v1/search": 1, "/v1/blocks/page-1/children": 2, "/v1/blocks/old-parent/children": 1, "/v1/blocks/page-2/children": 1}
    )
    search_request = next(request for request in requests_mock.request_history if request.method == "POST")
    assert search_request.json() == {
        "sort": {"direction": "descending", "timestamp": "last_edited_time"},
        "filter": {"property": "object", "value": "page"},
        "page_size": 100,
    }
    return output


@freeze_time("2024-06-01")
@pytest.mark.parametrize("start_date", ["2024-01-01T00:00:00.000Z", "2024-01-02T00:00:00.000Z"])
@pytest.mark.parametrize("state_shape", ["emitted", "legacy"])
def test_incremental_read_filters_old_blocks_after_traversing_children(requests_mock: Mocker, start_date: str, state_shape: str) -> None:
    config = {**CONFIG, "start_date": start_date}
    _mock_blocks(requests_mock, "2024-01-02T00:00:00.000Z")
    initial = _read_blocks(requests_mock, config, StateBuilder().with_stream_state("blocks", {}).build())
    initial_ids = ["nested-child", "boundary"]
    if start_date == CONFIG["start_date"]:
        initial_ids += ["old-parent", "old-sibling"]
    assert Counter(record.record.data["id"] for record in initial.records) == Counter(initial_ids)
    assert initial.most_recent_state.stream_state.__dict__["state"] == {"last_edited_time": "2024-01-03T00:00:00.000000Z"}

    _mock_blocks(requests_mock, "2024-01-04T00:00:00.000Z", add_new_block=True)
    state = [initial.state_messages[-1].state]
    if state_shape == "legacy":
        state = StateBuilder().with_stream_state("blocks", {"last_edited_time": "2024-01-03T00:00:00.000Z"}).build()
    updated = _read_blocks(requests_mock, config, state)
    # The cursor is inclusive: only the high-watermark record is expected to overlap.
    assert Counter(record.record.data["id"] for record in updated.records) == Counter(["nested-child", "boundary", "new-block"])
    assert updated.most_recent_state.stream_state.__dict__["state"] == {"last_edited_time": "2024-01-05T00:00:00.000000Z"}

    unchanged = _read_blocks(requests_mock, config, [updated.state_messages[-1].state])
    assert [record.record.data["id"] for record in unchanged.records] == ["new-block"]
    assert unchanged.most_recent_state.stream_state.__dict__["state"] == {"last_edited_time": "2024-01-05T00:00:00.000000Z"}

    full_refresh = _read_blocks(requests_mock, config, [], SyncMode.full_refresh)
    assert Counter(record.record.data["id"] for record in full_refresh.records) == Counter(initial_ids + ["new-block"])
