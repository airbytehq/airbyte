# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
from freezegun import freeze_time

from unit_tests.mock_server.helpers import read_stream


@freeze_time("2021-08-01T00:00:00Z")
@pytest.mark.parametrize("checkpoint", ["complete", "parent_only", "global_parent"])
def test_threads_resume_parent_state(token_config, requests_mock, checkpoint):
    config = {
        **token_config,
        "start_date": "2021-07-01T00:00:00Z",
        "end_date": "2021-08-01T00:00:00Z",
        "lookback_window": 7,
        "channel_filter": [],
        "join_channels": False,
    }
    requests_mock.get(
        "https://slack.com/api/conversations.list",
        json={"channels": [{"id": "C1", "name": "one", "is_member": True}, {"id": "C2", "name": "two", "is_member": True}]},
    )
    timestamps = {"C1": "1627516800.000000", "C2": "1627603200.000000"}
    for channel, ts in timestamps.items():
        requests_mock.get(f"https://slack.com/api/conversations.history?channel={channel}", json={"messages": [{"ts": ts}]})
        requests_mock.get(f"https://slack.com/api/conversations.replies?channel={channel}&ts={ts}", json={"messages": [{"ts": ts}]})
    first = read_stream(config, "threads")
    saved = first.most_recent_state.stream_state.__dict__
    assert {(r.record.data["channel_id"], r.record.data["ts"]) for r in first.records} == set(timestamps.items())
    assert len(first.records) == 2
    parent = saved["parent_state"]["channel_messages"]
    assert {s["partition"]["channel"]: s["cursor"]["float_ts"] for s in parent["states"]} == {
        channel: str(float(ts)) for channel, ts in timestamps.items()
    }
    if checkpoint == "parent_only":
        # An interrupted read can checkpoint parent progress before any child partitions complete.
        saved["states"] = []
        saved.pop("state", None)
    elif checkpoint == "global_parent":
        parent.pop("states")
        parent["use_global_cursor"] = True
    new_timestamps = {"C1": "1627689600.000000", "C2": "1627775990.000000"}
    for channel, ts in timestamps.items():
        new_ts = new_timestamps[channel]
        requests_mock.get(f"https://slack.com/api/conversations.history?channel={channel}", json={"messages": [{"ts": ts}, {"ts": new_ts}]})
        requests_mock.get(f"https://slack.com/api/conversations.replies?channel={channel}&ts={new_ts}", json={"messages": [{"ts": new_ts}]})
    requests_mock.reset_mock()
    second = read_stream(config, "threads", saved)
    history = [r.qs for r in requests_mock.request_history if r.path.endswith("conversations.history")]
    assert sorted(history, key=lambda q: q["channel"]) == [
        {
            "inclusive": ["true"],
            "limit": ["1000"],
            "channel": [channel.lower()],
            "oldest": [str(float(timestamps["C2"] if checkpoint == "global_parent" else ts) - 7 * 86400)],
            "latest": ["1627776000.0"],
        }
        for channel, ts in timestamps.items()
    ]
    # The seven-day overlap is emitted once alongside new replies, with no missing records.
    assert len(second.records) == 4
    assert {(r.record.data["channel_id"], r.record.data["ts"]) for r in second.records} == set(timestamps.items()) | set(
        new_timestamps.items()
    )
    parent_after = second.most_recent_state.stream_state.__dict__["parent_state"]["channel_messages"]
    assert parent_after["state"] == {"float_ts": "1627775990.0"}
    if checkpoint != "global_parent":
        assert {s["partition"]["channel"]: s["cursor"]["float_ts"] for s in parent_after["states"]} == {
            channel: str(float(ts)) for channel, ts in new_timestamps.items()
        }
