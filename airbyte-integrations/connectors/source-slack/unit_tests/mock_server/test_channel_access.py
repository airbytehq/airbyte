# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
from freezegun import freeze_time

from unit_tests.mock_server.helpers import read_stream


@freeze_time("2021-08-01T00:00:00Z")
@pytest.mark.parametrize("stream_name", ["channel_messages", "threads"])
@pytest.mark.parametrize("join_channels", [False, True])
def test_archived_channel_access(token_config, requests_mock, stream_name, join_channels):
    config = {
        **token_config,
        "start_date": "2021-07-01T00:00:00Z",
        "end_date": "2021-08-01T00:00:00Z",
        "lookback_window": 7,
        "channel_filter": [],
        "join_channels": join_channels,
        "include_archived_channels": True,
    }
    requests_mock.get(
        "https://slack.com/api/conversations.list",
        json={
            "channels": [
                {"id": "C1", "name": "archived-member", "is_member": True, "is_archived": True},
                {"id": "C2", "name": "archived-nonmember", "is_member": False, "is_archived": True},
                {"id": "C3", "name": "active-member", "is_member": True, "is_archived": False},
                {"id": "C4", "name": "active-nonmember", "is_member": False, "is_archived": False},
            ]
        },
    )
    join = requests_mock.post("https://slack.com/api/conversations.join", json={"ok": True, "channel": {}})
    for channel in ["C1", "C2", "C3", "C4"]:
        requests_mock.get(
            f"https://slack.com/api/conversations.history?channel={channel}", json={"messages": [{"ts": "1627516800.000000"}]}
        )
        requests_mock.get(
            f"https://slack.com/api/conversations.replies?channel={channel}&ts=1627516800.000000",
            json={"messages": [{"ts": "1627516800.000000"}]},
        )
    output = read_stream(config, stream_name)
    expected_channels = {"C1", "C3", "C4"} if join_channels else {"C1", "C3"}
    histories = [r for r in requests_mock.request_history if r.path.endswith("conversations.history")]
    assert {r.qs["channel"][0].upper() for r in histories} == expected_channels
    assert len(histories) == len(expected_channels)
    for request in histories:
        assert request.qs == {
            "inclusive": ["true"],
            "limit": ["1000"],
            "channel": request.qs["channel"],
            "oldest": ["1625097600.0"],
            "latest": ["1627776000.0"],
        }
    assert {(r.record.data["channel_id"], r.record.data["ts"]) for r in output.records} == {
        (channel, "1627516800.000000") for channel in expected_channels
    }
    assert len(output.records) == len(expected_channels)
    assert join.call_count == int(join_channels)
    if join_channels:
        assert join.last_request.json() == {"channel": "C4"}
    replies = [r.qs for r in requests_mock.request_history if r.path.endswith("conversations.replies")]
    assert sorted(replies, key=lambda q: q["channel"]) == (
        [{"channel": [channel.lower()], "ts": ["1627516800.000000"], "limit": ["1000"]} for channel in sorted(expected_channels)]
        if stream_name == "threads"
        else []
    )
