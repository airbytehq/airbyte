# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from copy import deepcopy

import pytest
from freezegun import freeze_time
from unit_tests.conftest import get_source

from airbyte_cdk.models import AirbyteStreamStateSerializer, ConfiguredAirbyteCatalogSerializer
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


def read_stream(config, stream_name, stream_state=None):
    state = StateBuilder().with_stream_state(stream_name, stream_state or {}).build()
    catalog = ConfiguredAirbyteCatalogSerializer.load(
        {
            "streams": [
                {
                    "stream": {"name": stream_name, "json_schema": {}, "supported_sync_modes": ["incremental"]},
                    "sync_mode": "incremental",
                    "destination_sync_mode": "append",
                }
            ]
        }
    )
    return read(get_source(config, stream_name, state), config=config, catalog=catalog, state=state)


def register_messages(requests_mock, channel, timestamps):
    messages = [{"ts": ts, "thread_ts": ts, "reply_count": 1} for ts in timestamps]
    requests_mock.get(
        f"https://slack.com/api/conversations.history?channel={channel}&limit=1000&inclusive=True",
        json={"ok": True, "messages": messages},
    )
    for message in messages:
        requests_mock.get(
            f"https://slack.com/api/conversations.replies?channel={channel}&limit=1000&ts={message['ts']}",
            json={"ok": True, "messages": [message]},
        )


@pytest.mark.parametrize("interrupted", [False, True])
def test_threads_resume_preserves_per_channel_parent_state(requests_mock, token_config, interrupted):
    config = {**token_config, "start_date": "2021-07-01T00:00:00Z", "end_date": "2021-08-03T00:00:00Z", "lookback_window": 7}
    timestamps = {"airbyte-for-beginners": "1627689600.000001", "good-reads": "1627603200.000002"}
    for channel, ts in timestamps.items():
        register_messages(requests_mock, channel, [ts])

    with freeze_time("2021-08-01T00:00:00Z"):
        first = read_stream(config, "threads")
    assert not first.errors
    assert sorted((r.record.data["channel_id"], r.record.data["ts"]) for r in first.records) == sorted(timestamps.items())
    saved_state = deepcopy(AirbyteStreamStateSerializer.dump(first.most_recent_state)["stream_state"])
    parent_state = saved_state["parent_state"]["channel_messages"]
    assert {s["partition"]["channel"]: s["cursor"] for s in parent_state["states"]} == {
        channel: {"float_ts": str(float(ts))} for channel, ts in timestamps.items()
    }
    if interrupted:
        saved_state["states"] = []
        saved_state["state"] = {}

    requests_mock.reset_mock()
    for channel, ts in timestamps.items():
        register_messages(requests_mock, channel, [ts, "1627776000.000003"])
    with freeze_time("2021-08-02T00:00:00Z"):
        second = read_stream(config, "threads", saved_state)
    assert not second.errors
    history = [r for r in requests_mock.request_history if r.path == "/api/conversations.history"]
    assert sorted((r.qs for r in history), key=lambda qs: qs["channel"]) == sorted(
        [
            {
                "channel": [channel],
                "limit": ["1000"],
                "inclusive": ["true"],
                "oldest": [str(float(ts) - 7 * 86400)],
                "latest": ["1627862400.0"],
            }
            for channel, ts in timestamps.items()
        ],
        key=lambda qs: qs["channel"],
    )
    assert sorted((r.record.data["channel_id"], r.record.data["ts"]) for r in second.records) == sorted(
        [(channel, ts) for channel, ts in timestamps.items()] + [(channel, "1627776000.000003") for channel in timestamps]
    )
    second_state = AirbyteStreamStateSerializer.dump(second.most_recent_state)["stream_state"]
    assert {s["partition"]["channel"]: s["cursor"] for s in second_state["parent_state"]["channel_messages"]["states"]} == {
        channel: {"float_ts": "1627776000.000003"} for channel in timestamps
    }


@pytest.mark.parametrize("stream_name", ["channel_messages", "threads"])
@pytest.mark.parametrize("join_channels", [False, True])
@freeze_time("2021-08-01T00:00:00Z")
def test_message_partitions_skip_only_unreadable_archived_channels(requests_mock, token_config, stream_name, join_channels):
    config = {
        **token_config,
        "start_date": "2021-07-01T00:00:00Z",
        "end_date": "2021-08-02T00:00:00Z",
        "channel_filter": [],
        "include_archived_channels": True,
        "join_channels": join_channels,
    }
    channels = [
        {"id": "archived-nonmember", "name": "archived-nonmember", "is_archived": True, "is_member": False},
        {"id": "archived-member", "name": "archived-member", "is_archived": True, "is_member": True},
        {"id": "active-member", "name": "active-member", "is_archived": False, "is_member": True},
        {"id": "active-nonmember", "name": "active-nonmember", "is_archived": False, "is_member": False},
    ]
    requests_mock.get(
        "https://slack.com/api/conversations.list?limit=999&types=public_channel&exclude_archived=false",
        json={"ok": True, "channels": channels},
        complete_qs=True,
    )
    requests_mock.post("https://slack.com/api/conversations.join", json={"ok": True})
    for channel in channels:
        register_messages(requests_mock, channel["id"], ["1627689600.000001"])
    requests_mock.get(
        "https://slack.com/api/conversations.history?channel=archived-nonmember&limit=1000&inclusive=True",
        json={"ok": False, "error": "not_in_channel"},
    )

    output = read_stream(config, stream_name)
    assert not output.errors
    expected_channels = ["active-member", "archived-member"] + (["active-nonmember"] if join_channels else [])
    assert sorted(r.record.data["channel_id"] for r in output.records) == sorted(expected_channels)
    history = [r for r in requests_mock.request_history if r.path == "/api/conversations.history"]
    assert sorted((r.qs for r in history), key=lambda qs: qs["channel"]) == sorted(
        [
            {"channel": [channel], "limit": ["1000"], "inclusive": ["true"], "oldest": ["1625097600.0"], "latest": ["1627776000.0"]}
            for channel in expected_channels
        ],
        key=lambda qs: qs["channel"],
    )
    joins = [r.json() for r in requests_mock.request_history if r.path == "/api/conversations.join"]
    assert joins == ([{"channel": "active-nonmember"}] if join_channels else [])
    if stream_name == "threads":
        replies = [r.qs for r in requests_mock.request_history if r.path == "/api/conversations.replies"]
        assert sorted(replies, key=lambda qs: qs["channel"]) == sorted(
            [{"channel": [channel], "limit": ["1000"], "ts": ["1627689600.000001"]} for channel in expected_channels],
            key=lambda qs: qs["channel"],
        )
