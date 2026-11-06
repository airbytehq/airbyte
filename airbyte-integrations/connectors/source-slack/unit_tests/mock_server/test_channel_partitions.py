# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
from freezegun import freeze_time

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from unit_tests.conftest import get_source


@freeze_time("2025-08-20T00:00:00Z")
@pytest.mark.parametrize("stream_name", ["channel_messages", "threads"])
@pytest.mark.parametrize("join_channels", [False, True])
def test_read_only_accessible_channel_partitions(requests_mock, token_config, stream_name, join_channels):
    config = {
        **token_config,
        "start_date": "2025-08-01T00:00:00Z",
        "end_date": "2025-08-20T00:00:00Z",
        "channel_filter": [],
        "include_archived_channels": True,
        "join_channels": join_channels,
    }
    channels = [
        {"id": "C_ACTIVE_MEMBER", "name": "active-member", "is_member": True, "is_archived": False},
        {"id": "C_ARCHIVED_MEMBER", "name": "archived-member", "is_member": True, "is_archived": True},
        {"id": "C_ACTIVE_NONMEMBER", "name": "active-nonmember", "is_member": False, "is_archived": False},
        {"id": "C_ARCHIVED_NONMEMBER", "name": "archived-nonmember", "is_member": False, "is_archived": True},
    ]
    requests_mock.get("https://slack.com/api/conversations.list", json={"ok": True, "channels": channels})
    joins = requests_mock.post("https://slack.com/api/conversations.join", json={"ok": True})

    def history_response(request, context):
        if request.qs["channel"] == ["c_archived_nonmember"]:
            return {"ok": False, "error": "not_in_channel"}
        return {"ok": True, "messages": [{"ts": "1755561600.000001", "reply_count": 1}]}

    requests_mock.get("https://slack.com/api/conversations.history", json=history_response)
    requests_mock.get("https://slack.com/api/conversations.replies", json={"ok": True, "messages": [{"ts": "1755561600.000001"}]})
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    output = read(get_source(config, stream_name), config=config, catalog=catalog)
    expected_channels = {"C_ACTIVE_MEMBER", "C_ARCHIVED_MEMBER"}
    if join_channels:
        expected_channels.add("C_ACTIVE_NONMEMBER")
    histories = [request for request in requests_mock.request_history if request.path.endswith("conversations.history")]
    assert sorted((request.qs for request in histories), key=lambda query: query["channel"]) == [
        {
            "channel": [channel.lower()],
            "inclusive": ["true"],
            "limit": ["1000"],
            "oldest": ["1754006400.0"],
            "latest": ["1755648000.0"],
        }
        for channel in sorted(expected_channels)
    ]
    assert {r.record.data["channel_id"] for r in output.records} == expected_channels
    assert len(output.records) == len(expected_channels)
    replies = [request.qs for request in requests_mock.request_history if request.path.endswith("conversations.replies")]
    assert sorted(replies, key=lambda query: query["channel"]) == (
        [{"channel": [channel.lower()], "ts": ["1755561600.000001"], "limit": ["1000"]} for channel in sorted(expected_channels)]
        if stream_name == "threads"
        else []
    )
    assert joins.call_count == int(join_channels)
    if join_channels:
        assert joins.last_request.json() == {"channel": "C_ACTIVE_NONMEMBER"}
