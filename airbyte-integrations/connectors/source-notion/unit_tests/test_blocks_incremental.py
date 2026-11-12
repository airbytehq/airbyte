# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from datetime import datetime

import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


@pytest.mark.parametrize("response_case", ["mixed", "old", "empty", "not_found"])
def test_blocks_incremental_filters_each_record_after_traversing_children(requests_mock, response_case):
    config = {"start_date": "2020-01-01T00:00:00.000Z", "credentials": {"auth_type": "token", "token": "abcd"}}
    old = "2024-05-01T00:00:00.000Z"
    cursor = "2024-06-01T00:00:00.000Z"
    new = "2024-07-01T00:00:00.000Z"

    def block(id, edited, children=False):
        return {"id": id, "type": "paragraph", "last_edited_time": edited, "has_children": children}

    def response(records):
        return {"object": "list", "results": records, "next_cursor": None, "has_more": False}

    requests_mock.post("https://api.notion.com/v1/search", json=response([{"id": "page-1", "last_edited_time": new}]))
    blocks = [block("old-parent", old, True), block("new-parent", new, True), block("boundary", cursor)]
    if response_case == "old":
        blocks = [block("old", old)]
    elif response_case != "mixed":
        blocks = []
    requests_mock.get(
        "https://api.notion.com/v1/blocks/page-1/children",
        json=response(blocks),
        status_code=404 if response_case == "not_found" else 200,
    )
    for parent in ["old-parent", "new-parent"]:
        requests_mock.get(
            f"https://api.notion.com/v1/blocks/{parent}/children",
            json=response([block(f"{parent}-old-child", old), block(f"{parent}-new-child", new)]),
        )
    catalog = CatalogBuilder().with_stream("blocks", SyncMode.incremental).build()
    state = StateBuilder().with_stream_state("blocks", {"state": {"last_edited_time": cursor}, "use_global_cursor": True}).build()
    output = read(get_source(config, state), config=config, catalog=catalog, state=state)

    expected_ids = (
        {"old-parent-new-child", "new-parent-new-child", "new-parent", "boundary"} if response_case == "mixed" else set()
    )
    assert {record.record.data["id"] for record in output.records} == expected_ids
    assert len(output.records) == len(expected_ids)
    emitted_state = output.most_recent_state.stream_state.__dict__
    assert emitted_state["use_global_cursor"] is True
    assert datetime.fromisoformat(emitted_state["state"]["last_edited_time"]) == datetime.fromisoformat(
        new if response_case == "mixed" else cursor
    )
