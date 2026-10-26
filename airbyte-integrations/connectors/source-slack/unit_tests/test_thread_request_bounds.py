# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from copy import deepcopy

import pytest
from freezegun import freeze_time

from airbyte_cdk.models import ConfiguredAirbyteCatalogSerializer
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


@freeze_time("2026-10-14T00:00:00Z")
@pytest.mark.parametrize("lookback,runtime_lookback", [(0, 0), (1, 0), (0, 600)])
def test_thread_requests_honor_saved_cursor_and_keep_paginated_boundary_replies(requests_mock, token_config, lookback, runtime_lookback):
    config = {
        **deepcopy(token_config),
        "start_date": "2025-12-26T00:00:00Z",
        "end_date": "2026-10-14T00:00:00Z",
        "channel_filter": ["airbyte-for-beginners"],
        "lookback_window": lookback,
        "channel_messages_window_size": 365,
        "threads_ignore_no_replies": True,
    }
    checkpoint = 1791849600
    expected_oldest = checkpoint - lookback * 86400 - runtime_lookback
    root = str(checkpoint - 3 * 86400)
    timestamps = [root, str(expected_oldest), str(checkpoint + 1), str(checkpoint + 2)]
    requests_mock.get(
        "https://slack.com/api/conversations.history",
        json={"ok": True, "messages": [{"ts": root, "thread_ts": root, "reply_count": 3}]},
    )

    def replies(request, context):
        oldest = float(request.qs.get("oldest", ["0"])[0])
        latest = float(request.qs.get("latest", ["9999999999"])[0])
        eligible = [ts for ts in timestamps if oldest <= float(ts) <= latest]
        offset = int(request.qs.get("cursor", ["0"])[0])
        next_cursor = str(offset + 1) if offset + 1 < len(eligible) else ""
        return {
            "ok": True,
            "messages": [{"ts": ts, "thread_ts": root} for ts in eligible[offset : offset + 1]],
            "has_more": bool(next_cursor),
            "response_metadata": {"next_cursor": next_cursor},
        }

    endpoint = requests_mock.get("https://slack.com/api/conversations.replies", json=replies)
    state = (
        StateBuilder()
        .with_stream_state(
            "threads",
            {
                "state": {"float_ts": str(checkpoint)},
                "use_global_cursor": True,
                "lookback_window": runtime_lookback,
                "parent_state": {"channel_messages": {"float_ts": "1766707200"}},
            },
        )
        .build()
    )
    catalog = ConfiguredAirbyteCatalogSerializer.load(
        {
            "streams": [
                {
                    "stream": {"name": "threads", "json_schema": {}, "supported_sync_modes": ["incremental"]},
                    "sync_mode": "incremental",
                    "destination_sync_mode": "append",
                }
            ]
        }
    )
    output = read(get_source(config, "threads", state), config=config, catalog=catalog, state=state)
    assert not output.errors
    assert {r.record.data["ts"] for r in output.records} == set(timestamps[1:])
    assert endpoint.call_count == 3
    for request in endpoint.request_history:
        assert float(request.qs["oldest"][0]) == expected_oldest
        assert float(request.qs["latest"][0]) == 1791936000
        assert request.qs["inclusive"] == ["true"]
    assert float(output.most_recent_state.stream_state.state["float_ts"]) == checkpoint + 2


@freeze_time("2026-10-14T00:00:00Z")
@pytest.mark.parametrize(
    "latest_reply,expected_requests,lookback",
    [
        ("1791849599.999999", 0, 0),
        ("1791849599.999999", 1, 1),
        ("1791849600.000000", 1, 0),
        ("1791849600.000001", 1, 0),
        (None, 1, 0),
        ("invalid", 1, 0),
        ("NaN", 1, 0),
        ("Infinity", 1, 0),
    ],
)
def test_thread_requests_skip_only_proven_older_replies(requests_mock, token_config, latest_reply, expected_requests, lookback):
    config = {
        **deepcopy(token_config),
        "start_date": "2025-12-26T00:00:00Z",
        "end_date": "2026-10-14T00:00:00Z",
        "channel_filter": ["airbyte-for-beginners"],
        "lookback_window": lookback,
        "channel_messages_window_size": 365,
        "threads_ignore_no_replies": True,
    }
    root = "1791763200"
    parent = {"ts": root, "thread_ts": root, "reply_count": 1}
    if latest_reply is not None:
        parent["latest_reply"] = latest_reply
    requests_mock.get("https://slack.com/api/conversations.history", json={"ok": True, "messages": [parent]})
    endpoint = requests_mock.get("https://slack.com/api/conversations.replies", json={"ok": True, "messages": []})
    state = (
        StateBuilder()
        .with_stream_state(
            "threads",
            {
                "state": {"float_ts": "1791849600"},
                "use_global_cursor": True,
                "parent_state": {"channel_messages": {"float_ts": "1766707200"}},
            },
        )
        .build()
    )
    catalog = ConfiguredAirbyteCatalogSerializer.load(
        {
            "streams": [
                {
                    "stream": {"name": "threads", "json_schema": {}, "supported_sync_modes": ["incremental"]},
                    "sync_mode": "incremental",
                    "destination_sync_mode": "append",
                }
            ]
        }
    )
    output = read(get_source(config, "threads", state), config=config, catalog=catalog, state=state)
    assert not output.errors
    assert not output.records
    assert endpoint.call_count == expected_requests
    parent_state = output.most_recent_state.stream_state.parent_state["channel_messages"]
    assert float(parent_state["states"][0]["cursor"]["float_ts"]) == float(root)


@freeze_time("2026-10-14T00:00:00Z")
@pytest.mark.parametrize("existing_partition", [False, True])
def test_thread_requests_preserve_initial_backfill_and_older_partition_cursors(requests_mock, token_config, existing_partition):
    config = {
        **deepcopy(token_config),
        "start_date": "2025-12-26T00:00:00Z",
        "end_date": "2026-10-14T00:00:00Z",
        "channel_filter": ["airbyte-for-beginners"],
        "lookback_window": 0,
        "channel_messages_window_size": 365,
        "threads_ignore_no_replies": True,
    }
    root = "1767225600"
    latest = "1777593600"
    requests_mock.get(
        "https://slack.com/api/conversations.history",
        json={"ok": True, "messages": [{"ts": root, "thread_ts": root, "reply_count": 1, "latest_reply": latest}]},
    )
    endpoint = requests_mock.get(
        "https://slack.com/api/conversations.replies", json={"ok": True, "messages": [{"ts": latest, "thread_ts": root}]}
    )
    if existing_partition:
        checkpoint = "1769904000"
        state = (
            StateBuilder()
            .with_stream_state(
                "threads",
                {
                    "state": {"float_ts": "1791849600"},
                    "use_global_cursor": False,
                    "states": [
                        {
                            "partition": {"float_ts": root, "parent_slice": {"channel": "airbyte-for-beginners", "parent_slice": {}}},
                            "cursor": {"float_ts": checkpoint},
                        }
                    ],
                    "parent_state": {"channel_messages": {"float_ts": "1766707200"}},
                },
            )
            .build()
        )
    else:
        checkpoint = "1766707200"
        state = StateBuilder().build()
    catalog = ConfiguredAirbyteCatalogSerializer.load(
        {
            "streams": [
                {
                    "stream": {"name": "threads", "json_schema": {}, "supported_sync_modes": ["incremental"]},
                    "sync_mode": "incremental",
                    "destination_sync_mode": "append",
                }
            ]
        }
    )
    output = read(get_source(config, "threads", state), config=config, catalog=catalog, state=state)
    assert not output.errors
    assert {r.record.data["ts"] for r in output.records} == {latest}
    assert endpoint.call_count == 1
    assert float(endpoint.request_history[0].qs["oldest"][0]) == float(checkpoint)
