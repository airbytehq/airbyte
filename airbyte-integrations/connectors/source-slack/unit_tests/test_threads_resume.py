# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import re

import freezegun
import pytest

from airbyte_cdk.models import ConfiguredAirbyteCatalogSerializer
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


NOW = "2024-03-20T00:00:00Z"  # 1710892800
START_DATE = "2024-01-01T00:00:00Z"  # 1704067200
LOOKBACK_DAYS = 7  # 604800 seconds

CHANNELS = [
    {"id": "C1", "name": "c1", "is_member": True, "is_archived": False},
    {"id": "C2", "name": "c2", "is_member": True, "is_archived": False},
]
MESSAGES = {
    "C1": [{"ts": "1709251200.000100", "reply_count": 1}],  # 2024-03-01
    "C2": [{"ts": "1710460800.000200", "reply_count": 1}],  # 2024-03-15
}


def _catalog(stream_name):
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
    token_config.pop("end_date")
    token_config.update({"start_date": START_DATE, "lookback_window": LOOKBACK_DAYS, "channel_filter": [], **overrides})
    return token_config


def _mock_slack(requests_mock, channels):
    requests_mock.register_uri("GET", re.compile(r"https://slack\.com/api/conversations\.list.*"), json={"channels": channels})

    def history(request, context):
        channel = request.qs["channel"][0].upper()
        if any(c["id"] == channel and not c["is_member"] for c in channels):
            return {"ok": False, "error": "not_in_channel"}
        return {"ok": True, "messages": MESSAGES.get(channel, [])}

    requests_mock.register_uri("GET", re.compile(r"https://slack\.com/api/conversations\.history.*"), json=history)
    requests_mock.register_uri(
        "GET",
        re.compile(r"https://slack\.com/api/conversations\.replies.*"),
        json=lambda request, context: {"ok": True, "messages": [{"ts": request.qs["ts"][0]}]},
    )


def _read(stream_name, config, stream_state=None):
    state = StateBuilder().with_stream_state(stream_name, stream_state).build() if stream_state else StateBuilder().build()
    return read(get_source(config, stream_name, state), config=config, catalog=_catalog(stream_name), state=state)


def _history_requests(requests_mock):
    """(channel, oldest) of every conversations.history request, in a stable order."""
    return sorted(
        (request.qs["channel"][0].upper(), request.qs["oldest"][0]) for request in requests_mock.request_history if "history" in request.url
    )


def _parent_cursors(output):
    parent_state = output.most_recent_state.stream_state.parent_state["channel_messages"]
    return {state["partition"]["channel"]: state["cursor"]["float_ts"] for state in parent_state["states"]}


def _channel_messages_state(cursors):
    return {
        "use_global_cursor": False,
        "states": [
            {"partition": {"channel": channel, "parent_slice": {}}, "cursor": {"float_ts": cursor}} for channel, cursor in cursors.items()
        ],
        "lookback_window": 0,
        "parent_state": {},
    }


@freezegun.freeze_time(NOW)
def test_threads_second_read_resumes_each_channel_from_its_own_cursor(requests_mock, token_config):
    config = _config(token_config)
    _mock_slack(requests_mock, CHANNELS)

    first_read = _read("threads", config)
    assert _history_requests(requests_mock) == [("C1", "1704067200.0"), ("C2", "1704067200.0")]
    assert _parent_cursors(first_read) == {"C1": "1709251200.0001", "C2": "1710460800.0002"}

    requests_mock.reset_mock()
    second_read = _read("threads", config, first_read.most_recent_state.stream_state.__dict__)

    # Each channel restarts at its own saved cursor minus the 7-day lookback window, so the newest
    # parent message of each channel is the only overlap between the two reads.
    assert _history_requests(requests_mock) == [("C1", "1708646400.0001"), ("C2", "1709856000.0002")]
    assert sorted((record.record.data["channel_id"], record.record.data["ts"]) for record in second_read.records) == [
        ("C1", "1709251200.000100"),
        ("C2", "1710460800.000200"),
    ]
    assert _parent_cursors(second_read) == {"C1": "1709251200.0001", "C2": "1710460800.0002"}


@freezegun.freeze_time(NOW)
def test_threads_read_after_interrupted_attempt_keeps_per_channel_parent_cursors(requests_mock, token_config):
    """
    State of an attempt that stopped after reading channel history but before any thread partition was
    checkpointed: `parent_state` has a cursor per channel and the threads stream itself has none.
    """
    config = _config(token_config)
    _mock_slack(requests_mock, CHANNELS)
    interrupted_state = {
        "use_global_cursor": False,
        "states": [],
        "lookback_window": 0,
        "parent_state": {"channel_messages": _channel_messages_state({"C1": "1709251200.0001", "C2": "1710460800.0002"})},
    }

    output = _read("threads", config, interrupted_state)

    assert _history_requests(requests_mock) == [("C1", "1708646400.0001"), ("C2", "1709856000.0002")]
    assert _parent_cursors(output) == {"C1": "1709251200.0001", "C2": "1710460800.0002"}


@pytest.mark.parametrize("stream_name", ["channel_messages", "threads"])
@freezegun.freeze_time(NOW)
def test_archived_channels_the_bot_is_not_a_member_of_are_not_requested(requests_mock, token_config, stream_name):
    config = _config(token_config, join_channels=True, include_archived_channels=True)
    channels = CHANNELS + [
        {"id": "CARCHIVED", "name": "archived", "is_member": False, "is_archived": True},
        {"id": "CARCHIVEDMEMBER", "name": "archived-member", "is_member": True, "is_archived": True},
    ]
    _mock_slack(requests_mock, channels)

    output = _read(stream_name, config)

    # The archived channel the bot already belongs to is still read; the one it cannot join is not.
    assert _history_requests(requests_mock) == [("C1", "1704067200.0"), ("C2", "1704067200.0"), ("CARCHIVEDMEMBER", "1704067200.0")]
    assert sorted((record.record.data["channel_id"], record.record.data["ts"]) for record in output.records) == [
        ("C1", "1709251200.000100"),
        ("C2", "1710460800.000200"),
    ]
    assert output.errors == []
    assert not any("not_in_channel" in log.log.message for log in output.logs)
