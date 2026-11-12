# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from copy import deepcopy
from urllib.parse import parse_qs, urlparse

import freezegun
import pytest

from airbyte_cdk.models import ConfiguredAirbyteCatalogSerializer
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


NOW = "2021-07-30T00:00:00Z"
START_DATE = "2021-07-01T00:00:00Z"
START_DATE_TS = 1625097600.0
NOW_TS = 1627603200.0
ONE_DAY = 86400.0  # the configured lookback_window is 1 day

JUL_03 = 1625270400.0
JUL_10 = 1625875200.0
JUL_20 = 1626739200.0


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


def _config(token_config):
    config = deepcopy(token_config)
    config["start_date"] = START_DATE
    config["channel_filter"] = []
    config.pop("end_date", None)
    return config


def _mock_slack(requests_mock, channels, messages_by_channel):
    """Serve conversations.list/history/replies; history honours the `oldest`/`latest` bounds like the Slack API does."""

    def history(request, context):
        channel = request.qs["channel"][0].upper()
        oldest, latest = float(request.qs["oldest"][0]), float(request.qs["latest"][0])
        return {
            "ok": True,
            "messages": [
                {"ts": str(ts), "thread_ts": str(ts), "reply_count": 1}
                for ts in messages_by_channel.get(channel, [])
                if oldest <= ts <= latest
            ],
        }

    def replies(request, context):
        ts = float(request.qs["ts"][0])
        return {"ok": True, "messages": [{"ts": str(ts)}, {"ts": str(ts + 60)}]}

    requests_mock.register_uri("GET", "https://slack.com/api/conversations.list", json={"ok": True, "channels": channels})
    requests_mock.register_uri("GET", "https://slack.com/api/conversations.history", json=history)
    requests_mock.register_uri("GET", "https://slack.com/api/conversations.replies", json=replies)


def _read(requests_mock, stream_name, config, state=None):
    """Run a real read and return (output, history requests as (channel, oldest, latest), replies requests as (channel, ts))."""
    requests_mock.reset_mock()
    state = state or StateBuilder().build()
    with freezegun.freeze_time(NOW):
        output = read(get_source(config, stream_name, state), config=config, catalog=_catalog(stream_name), state=state)

    def queries(method):
        return [parse_qs(urlparse(r.url).query) for r in requests_mock.request_history if r.url.startswith(f"https://slack.com/api/{method}")]

    history = sorted((q["channel"][0], float(q["oldest"][0]), float(q["latest"][0])) for q in queries("conversations.history"))
    replies = sorted((q["channel"][0], float(q["ts"][0])) for q in queries("conversations.replies"))
    return output, history, replies


def _thread_records(output):
    return sorted((r.record.data["channel_id"], r.record.data["float_ts"]) for r in output.records)


def _channel_cursors(output):
    parent_state = output.most_recent_state.stream_state.parent_state["channel_messages"]
    return {s["partition"]["channel"]: float(s["cursor"]["float_ts"]) for s in parent_state["states"]}


def _keep_only_first_thread(state):
    """The state of a sync interrupted after its first thread: channel cursors are saved, most thread cursors are not."""
    state = deepcopy(state)
    state["states"] = [s for s in state["states"] if float(s["partition"]["float_ts"]) == JUL_03]
    assert len(state["states"]) == 1
    state["state"] = state["states"][0]["cursor"]
    return state


@pytest.mark.parametrize(
    "prepare_state",
    (lambda state: state, _keep_only_first_thread),
    ids=["state_of_completed_sync", "state_of_interrupted_sync"],
)
def test_threads_resume_each_channel_from_its_own_saved_cursor(requests_mock, token_config, prepare_state):
    config = _config(token_config)
    channels = [{"id": "A", "name": "a", "is_member": True}, {"id": "B", "name": "b", "is_member": True}]
    _mock_slack(requests_mock, channels, {"A": [JUL_03, JUL_20], "B": [JUL_10]})

    first_output, first_history, _ = _read(requests_mock, "threads", config)

    assert first_history == [("A", START_DATE_TS, NOW_TS), ("B", START_DATE_TS, NOW_TS)]
    assert _thread_records(first_output) == [("A", JUL_03), ("A", JUL_03 + 60), ("A", JUL_20), ("A", JUL_20 + 60), ("B", JUL_10), ("B", JUL_10 + 60)]
    assert _channel_cursors(first_output) == {"A": JUL_20, "B": JUL_10}

    saved_state = prepare_state(first_output.most_recent_state.stream_state.__dict__)
    second_output, second_history, second_replies = _read(
        requests_mock, "threads", config, StateBuilder().with_stream_state("threads", saved_state).build()
    )

    # Each channel is requested from its own cursor minus the 1-day lookback window, not from start_date
    # and not from a cursor shared by all channels.
    assert second_history == [("A", JUL_20 - ONE_DAY, NOW_TS), ("B", JUL_10 - ONE_DAY, NOW_TS)]
    # Only the lookback overlap (the last message of each channel) is read again; the Jul 3 thread is not.
    assert second_replies == [("A", JUL_20), ("B", JUL_10)]
    assert _thread_records(second_output) == [("A", JUL_20), ("A", JUL_20 + 60), ("B", JUL_10), ("B", JUL_10 + 60)]
    assert _channel_cursors(second_output) == {"A": JUL_20, "B": JUL_10}


ALL_BUT_ARCHIVED_NOT_MEMBER = ["ACTIVE", "ARCHIVED_MEMBER", "JOINABLE"]
ALL_CHANNELS = ["ACTIVE", "ARCHIVED_MEMBER", "ARCHIVED_NOT_MEMBER", "JOINABLE"]


@pytest.mark.parametrize(
    "stream_name, api_token, expected_channels",
    (
        # A bot can neither join an archived channel nor read a channel it is not a member of.
        ("channel_messages", "xoxb-bot-token", ALL_BUT_ARCHIVED_NOT_MEMBER),
        ("threads", "xoxb-bot-token", ALL_BUT_ARCHIVED_NOT_MEMBER),
        # A user token can read public channels without membership, so nothing is dropped for it.
        ("channel_messages", "xoxp-user-token", ALL_CHANNELS),
        ("threads", "xoxp-user-token", ALL_CHANNELS),
    ),
)
def test_archived_channels_a_bot_cannot_join_are_not_requested(requests_mock, token_config, stream_name, api_token, expected_channels):
    config = _config(token_config)
    config["join_channels"] = True
    config["include_archived_channels"] = True
    config["credentials"]["api_token"] = api_token
    channels = [
        {"id": "ACTIVE", "name": "active", "is_member": True, "is_archived": False},
        {"id": "JOINABLE", "name": "joinable", "is_member": False, "is_archived": False},
        {"id": "ARCHIVED_MEMBER", "name": "archived-member", "is_member": True, "is_archived": True},
        {"id": "ARCHIVED_NOT_MEMBER", "name": "archived-not-member", "is_member": False, "is_archived": True},
    ]
    requests_mock.register_uri("POST", "https://slack.com/api/conversations.join", json={"ok": True})
    _mock_slack(requests_mock, channels, {channel["id"]: [JUL_10] for channel in channels})

    output, history, replies = _read(requests_mock, stream_name, config)

    assert history == [(channel, START_DATE_TS, NOW_TS) for channel in expected_channels]
    assert replies == ([(channel, JUL_10) for channel in expected_channels] if stream_name == "threads" else [])
    assert sorted({r.record.data["channel_id"] for r in output.records}) == expected_channels
    assert output.errors == []
