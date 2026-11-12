#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#
from collections import Counter

import pytest
from freezegun import freeze_time

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


OLD = "2024-01-01T00:00:00.000Z"
BOUNDARY = "2024-01-02T00:00:00.000Z"
UPDATED = "2024-01-03T00:00:00.000Z"
CONFIG = {
    "start_date": "2020-01-01T00:00:00.000Z",
    "credentials": {"auth_type": "token", "token": "test-token"},
    "num_workers": 1,
}


def _record(record_id: str, edited: str, has_children: bool = False) -> dict:
    return {
        "object": "block",
        "id": record_id,
        "type": "paragraph",
        "paragraph": {"rich_text": []},
        "last_edited_time": edited,
        "has_children": has_children,
        "parent": {"type": "page_id", "page_id": "page-1"},
    }


def _response(records: list[dict], next_cursor: str | None = None) -> dict:
    return {"object": "list", "results": records, "has_more": next_cursor is not None, "next_cursor": next_cursor}


def _mock_blocks(requests_mock, child_edited: str) -> None:
    requests_mock.post(
        "https://api.notion.com/v1/search",
        json=_response(
            [{"object": "page", "id": page_id, "last_edited_time": UPDATED, "properties": {}} for page_id in ("page-1", "page-2")]
        ),
    )
    requests_mock.get(
        "https://api.notion.com/v1/blocks/page-1/children?page_size=100",
        json=_response([_record("old-parent", OLD, has_children=True), _record("old-sibling", OLD)], "next-page"),
        complete_qs=True,
    )
    requests_mock.get(
        "https://api.notion.com/v1/blocks/old-parent/children?page_size=100",
        json=_response([_record("nested-child", child_edited)]),
        complete_qs=True,
    )
    requests_mock.get(
        "https://api.notion.com/v1/blocks/page-1/children?page_size=100&start_cursor=next-page",
        json=_response([_record("boundary-block", BOUNDARY)]),
        complete_qs=True,
    )
    requests_mock.get(
        "https://api.notion.com/v1/blocks/page-2/children?page_size=100",
        json=_response([_record("other-page-block", OLD)]),
        complete_qs=True,
    )


def _read_blocks(state=None, config=None, sync_mode=SyncMode.incremental):
    config = config or CONFIG
    catalog = CatalogBuilder().with_stream("blocks", sync_mode).build()
    return read(get_source(config, state), config=config, catalog=catalog, state=state)


@freeze_time("2024-01-04")
@pytest.mark.parametrize("legacy_state", [False, True], ids=["emitted-state", "legacy-flat-state"])
def test_incremental_read_filters_old_blocks_without_pruning_children(requests_mock, legacy_state: bool) -> None:
    _mock_blocks(requests_mock, BOUNDARY)
    first = _read_blocks()
    assert Counter(record.record.data["id"] for record in first.records) == Counter(
        ["old-parent", "old-sibling", "nested-child", "boundary-block", "other-page-block"]
    )
    stream_state = first.most_recent_state.stream_state.__dict__
    assert stream_state["state"] == {"last_edited_time": "2024-01-02T00:00:00.000000Z"}

    state = StateBuilder().with_stream_state("blocks", {"last_edited_time": BOUNDARY} if legacy_state else stream_state).build()
    _mock_blocks(requests_mock, UPDATED)
    requests_mock.reset_mock()
    resumed = _read_blocks(state)
    # The inclusive cursor intentionally repeats the boundary, but no older blocks.
    assert Counter(record.record.data["id"] for record in resumed.records) == Counter(["nested-child", "boundary-block"])
    assert resumed.most_recent_state.stream_state.__dict__["state"] == {"last_edited_time": "2024-01-03T00:00:00.000000Z"}
    assert Counter((request.method, request.url) for request in requests_mock.request_history) == Counter(
        [
            ("POST", "https://api.notion.com/v1/search"),
            ("GET", "https://api.notion.com/v1/blocks/page-1/children?page_size=100"),
            ("GET", "https://api.notion.com/v1/blocks/old-parent/children?page_size=100"),
            ("GET", "https://api.notion.com/v1/blocks/page-1/children?start_cursor=next-page&page_size=100"),
            ("GET", "https://api.notion.com/v1/blocks/page-2/children?page_size=100"),
        ]
    )
    refreshed = _read_blocks(sync_mode=SyncMode.full_refresh)
    assert Counter(record.record.data["id"] for record in refreshed.records) == Counter(
        ["old-parent", "old-sibling", "nested-child", "boundary-block", "other-page-block"]
    )


@freeze_time("2024-01-04")
def test_start_date_filters_old_blocks_after_traversing_children(requests_mock) -> None:
    _mock_blocks(requests_mock, UPDATED)
    output = _read_blocks(config={**CONFIG, "start_date": BOUNDARY})
    assert Counter(record.record.data["id"] for record in output.records) == Counter(["nested-child", "boundary-block"])
    assert output.most_recent_state.stream_state.__dict__["state"] == {"last_edited_time": "2024-01-03T00:00:00.000000Z"}
