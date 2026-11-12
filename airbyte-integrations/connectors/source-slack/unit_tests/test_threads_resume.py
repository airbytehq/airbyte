#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#
"""
Mock-server reads covering two `threads` / `channel_messages` behaviours:

* a `threads` sync resumed from saved state must request `conversations.history`
  for each channel from that channel's saved `channel_messages` cursor (minus the
  lookback window), not from `start_date`;
* with `join_channels: true` and `include_archived_channels: true`, archived
  channels the bot is not a member of must not become message/thread partitions,
  because the bot cannot join archived channels.
"""

from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlparse

import freezegun
import pytest

from airbyte_cdk.models import ConfiguredAirbyteCatalogSerializer
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


NOW = datetime(2026, 11, 1, tzinfo=timezone.utc)
START_DATE = "2026-01-01T00:00:00Z"
LOOKBACK_DAYS = 7

CHANNEL_A = "C0000000A"
CHANNEL_B = "C0000000B"
ARCHIVED_CHANNEL = "C000ARCHV"

# Per-channel channel_messages cursors saved under parent_state before the restart.
CHANNEL_A_CURSOR = datetime(2026, 10, 20, tzinfo=timezone.utc).timestamp()
CHANNEL_B_CURSOR = datetime(2026, 10, 25, tzinfo=timezone.utc).timestamp()


def _catalog(stream_name: str):
    return ConfiguredAirbyteCatalogSerializer.load(
        {
            "streams": [
                {
                    "stream": {"name": stream_name, "json_schema": {}, "supported_sync_modes": ["full_refresh", "incremental"]},
                    "sync_mode": "incremental",
                    "destination_sync_mode": "append",
                }
            ]
        }
    )


def _config(token_config, **overrides):
    token_config.update(
        {
            "start_date": START_DATE,
            "lookback_window": LOOKBACK_DAYS,
            "join_channels": True,
            "include_archived_channels": True,
            "channel_filter": [],
        }
    )
    token_config.pop("end_date", None)
    token_config.update(overrides)
    return token_config


def _mock_channels(requests_mock, channels):
    requests_mock.get(
        "https://slack.com/api/conversations.list?limit=999&types=public_channel&exclude_archived=false",
        json={"channels": channels},
    )
    requests_mock.post("https://slack.com/api/conversations.join", json={"ok": True, "channel": {}})


def _history_requests(requests_mock):
    return [r for r in requests_mock.request_history if urlparse(r.url).path == "/api/conversations.history"]


def _oldest_by_channel(requests_mock):
    oldest = {}
    for request in _history_requests(requests_mock):
        query = parse_qs(urlparse(request.url).query)
        channel = query["channel"][0]
        oldest[channel] = min(oldest.get(channel, float("inf")), float(query["oldest"][0]))
    return oldest


def _threads_state_with_parent(threads_cursor_state):
    parent_state = {
        "channel_messages": {
            "use_global_cursor": False,
            "states": [
                {"partition": {"channel": CHANNEL_A, "parent_slice": {}}, "cursor": {"float_ts": str(CHANNEL_A_CURSOR)}},
                {"partition": {"channel": CHANNEL_B, "parent_slice": {}}, "cursor": {"float_ts": str(CHANNEL_B_CURSOR)}},
            ],
            "state": {"float_ts": str(CHANNEL_A_CURSOR)},
            "lookback_window": 0,
            "parent_state": {},
        }
    }
    return {**threads_cursor_state, "parent_state": parent_state}


@freezegun.freeze_time(NOW)
@pytest.mark.parametrize(
    "threads_cursor_state",
    [
        pytest.param(
            # The per-partition cursor fell back to a global cursor (too many thread partitions).
            {"use_global_cursor": True, "state": {"float_ts": str(CHANNEL_A_CURSOR)}, "lookback_window": 0},
            id="global_threads_cursor",
        ),
        pytest.param(
            {
                "use_global_cursor": False,
                "states": [
                    {
                        "partition": {"float_ts": "1792000000.0", "parent_slice": {"channel": CHANNEL_A, "parent_slice": {}}},
                        "cursor": {"float_ts": str(int(CHANNEL_A_CURSOR))},
                    }
                ],
                "state": {"float_ts": str(int(CHANNEL_A_CURSOR))},
                "lookback_window": 0,
            },
            id="per_partition_threads_cursor",
        ),
    ],
)
def test_threads_resume_requests_history_from_saved_channel_cursors(token_config, requests_mock, threads_cursor_state):
    config = _config(token_config)
    _mock_channels(
        requests_mock,
        [
            {"id": CHANNEL_A, "name": "channel-a", "is_member": True, "is_archived": False},
            {"id": CHANNEL_B, "name": "channel-b", "is_member": True, "is_archived": False},
        ],
    )
    requests_mock.get("https://slack.com/api/conversations.history", json={"ok": True, "messages": []})

    state = StateBuilder().with_stream_state("threads", _threads_state_with_parent(threads_cursor_state)).build()
    output = read(get_source(config, "threads", state), config=config, catalog=_catalog("threads"), state=state)

    assert not output.errors
    lookback = timedelta(days=LOOKBACK_DAYS).total_seconds()
    assert _oldest_by_channel(requests_mock) == {
        CHANNEL_A: CHANNEL_A_CURSOR - lookback,
        CHANNEL_B: CHANNEL_B_CURSOR - lookback,
    }


@freezegun.freeze_time(NOW)
@pytest.mark.parametrize("stream_name", ["channel_messages", "threads"])
def test_archived_non_member_channels_are_not_partitioned_when_joining(token_config, requests_mock, stream_name):
    config = _config(token_config, start_date="2026-10-01T00:00:00Z")
    _mock_channels(
        requests_mock,
        [
            {"id": CHANNEL_A, "name": "channel-a", "is_member": True, "is_archived": False},
            {"id": CHANNEL_B, "name": "channel-b", "is_member": False, "is_archived": False},
            {"id": ARCHIVED_CHANNEL, "name": "archived", "is_member": False, "is_archived": True},
        ],
    )
    requests_mock.get(
        "https://slack.com/api/conversations.history",
        json={"ok": True, "messages": [{"ts": "1792000000.000100", "reply_count": 1, "thread_ts": "1792000000.000100"}]},
    )
    requests_mock.get("https://slack.com/api/conversations.replies", json={"ok": True, "messages": [{"ts": "1792000000.000100"}]})

    output = read(get_source(config, stream_name), config=config, catalog=_catalog(stream_name))

    assert not output.errors
    assert {parse_qs(urlparse(r.url).query)["channel"][0] for r in _history_requests(requests_mock)} == {CHANNEL_A, CHANNEL_B}
    assert {record.record.data["channel_id"] for record in output.records} == {CHANNEL_A, CHANNEL_B}
