# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from datetime import datetime

import pytest

from airbyte_cdk.models import AirbyteStreamStateSerializer, ConfiguredAirbyteCatalogSerializer
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


@pytest.mark.parametrize("response_kind", ["mixed", "empty", "not_found"])
def test_blocks_incremental_filters_records_after_traversing_children(requests_mock, response_kind):
    config = {"start_date": "2020-01-01T00:00:00.000Z", "credentials": {"auth_type": "token", "token": "abcd"}}
    old = "2022-01-01T00:00:00.000Z"
    checkpoint = "2022-01-02T00:00:00.000Z"
    new = "2022-01-03T00:00:00.000Z"

    def block(block_id, edited, has_children=False):
        return {
            "object": "block",
            "id": block_id,
            "type": "paragraph",
            "paragraph": {"rich_text": []},
            "last_edited_time": edited,
            "has_children": has_children,
        }

    def response(records):
        return {"object": "list", "results": records, "has_more": False, "next_cursor": None}

    requests_mock.post(
        "https://api.notion.com/v1/search",
        json=response([{"object": "page", "id": "page-1", "last_edited_time": old, "properties": {}}]),
    )
    url = "https://api.notion.com/v1/blocks/page-1/children?page_size=100"
    if response_kind == "not_found":
        requests_mock.get(url, status_code=404, json={"object": "error", "code": "object_not_found", "message": "Not found"})
    else:
        requests_mock.get(
            url,
            json=response([block("old-parent", old, True), block("new-block", new)] if response_kind == "mixed" else []),
        )
    if response_kind == "mixed":
        requests_mock.get(
            "https://api.notion.com/v1/blocks/old-parent/children?page_size=100",
            json=response([block("old-child", old), block("new-child", new)]),
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
    state = StateBuilder().with_stream_state("blocks", {"last_edited_time": checkpoint}).build()
    output = read(get_source(config, state), config=config, catalog=catalog, state=state)

    assert not output.errors
    assert [message.record.data["id"] for message in output.records] == (["new-child", "new-block"] if response_kind == "mixed" else [])
    emitted_cursor = AirbyteStreamStateSerializer.dump(output.most_recent_state)["stream_state"]["state"]["last_edited_time"]
    assert datetime.fromisoformat(emitted_cursor) == datetime.fromisoformat(new if response_kind == "mixed" else checkpoint)
