# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any, Optional

import pytest
import requests_mock
from freezegun import freeze_time
from unit_tests.conftest import get_source

from airbyte_cdk.models import AirbyteStateMessage, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read


CONFIG = {
    "start_date": "2024-01-02T00:00:00.000Z",
    "credentials": {"auth_type": "token", "token": "test-token"},
    "num_workers": 1,
}
BASE_URL = "https://api.notion.com/v1"


def block(block_id: str, edited_at: str, parent_id: str = "page-1", has_children: bool = False) -> dict[str, Any]:
    return {
        "object": "block",
        "id": block_id,
        "type": "paragraph",
        "paragraph": {"rich_text": []},
        "last_edited_time": edited_at,
        "has_children": has_children,
        "parent": {"type": "block_id", "block_id": parent_id},
    }


def response(records: list[dict[str, Any]], next_cursor: Optional[str] = None) -> dict[str, Any]:
    return {"object": "list", "results": records, "has_more": bool(next_cursor), "next_cursor": next_cursor}


def read_blocks(
    records: list[dict[str, Any]],
    children: list[dict[str, Any]],
    state: Optional[list[AirbyteStateMessage]] = None,
    sync_mode: SyncMode = SyncMode.incremental,
) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream("blocks", sync_mode).build()
    with requests_mock.Mocker() as http:
        http.post(
            f"{BASE_URL}/search",
            json=response([{"object": "page", "id": "page-1", "last_edited_time": "2024-01-05T00:00:00.000Z", "properties": {}}]),
        )
        http.get(f"{BASE_URL}/blocks/page-1/children?page_size=100", json=response(records[:1], "next-page"), complete_qs=True)
        http.get(
            f"{BASE_URL}/blocks/page-1/children?page_size=100&start_cursor=next-page",
            json=response(records[1:]),
            complete_qs=True,
        )
        http.get(f"{BASE_URL}/blocks/ancestor/children?page_size=100", json=response(children), complete_qs=True)
        output = read(get_source(CONFIG, state), CONFIG, catalog, state=state)
        history = [(request.method, request.path_url) for request in http.request_history]
    assert not output.errors
    assert sorted(history) == sorted(
        [
            ("POST", "/v1/search"),
            ("GET", "/v1/blocks/page-1/children?page_size=100"),
            ("GET", "/v1/blocks/page-1/children?start_cursor=next-page&page_size=100"),
            ("GET", "/v1/blocks/ancestor/children?page_size=100"),
        ]
    )
    return output


@freeze_time("2024-01-10")
@pytest.mark.parametrize("ancestor_time", ["2024-01-01T00:00:00.000Z", "2024-01-02T00:00:00.000Z"])
def test_incremental_read_resumes_without_reemitting_unchanged_blocks(ancestor_time: str) -> None:
    ancestor = block("ancestor", ancestor_time, has_children=True)
    boundary = block("boundary", "2024-01-03T00:00:00.000Z")
    first = read_blocks(
        [ancestor, boundary],
        [block("child", "2024-01-02T00:00:00.000Z", "ancestor")],
    )
    expected_first = ["child", "boundary"] if ancestor_time < CONFIG["start_date"] else ["child", "ancestor", "boundary"]
    assert [message.record.data["id"] for message in first.records] == expected_first
    saved_state = first.most_recent_state.stream_state.__dict__
    assert saved_state["state"] == {"last_edited_time": "2024-01-03T00:00:00.000000Z"}

    second = read_blocks(
        [ancestor, boundary, block("new", "2024-01-05T00:00:00.000Z")],
        [block("child", "2024-01-04T00:00:00.000Z", "ancestor"), block("old-child", "2024-01-02T00:00:00.000Z", "ancestor")],
        state=[message.state for message in first.state_messages],
    )
    # The cursor is inclusive: only the boundary may repeat, and an old ancestor must not hide an updated child.
    assert [message.record.data["id"] for message in second.records] == ["child", "boundary", "new"]
    assert [message.record.data["parent"]["sequence_number"] for message in second.records] == [0, 1, 2]
    assert second.most_recent_state.stream_state.__dict__["state"] == {"last_edited_time": "2024-01-05T00:00:00.000000Z"}


@freeze_time("2024-01-10")
def test_full_refresh_includes_unchanged_blocks() -> None:
    output = read_blocks(
        [block("ancestor", "2024-01-02T00:00:00.000Z", has_children=True), block("sibling", "2024-01-03T00:00:00.000Z")],
        [block("child", "2024-01-02T00:00:00.000Z", "ancestor")],
        sync_mode=SyncMode.full_refresh,
    )
    assert [message.record.data["id"] for message in output.records] == ["child", "ancestor", "sibling"]
