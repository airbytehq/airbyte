# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlparse

import pytest

from airbyte_cdk.models import ConfiguredAirbyteCatalogSerializer
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


DAY = 86400
NOW = int(datetime.now(timezone.utc).timestamp())
START_DATE = NOW - 30 * DAY
# Channel A stopped ten days ago, channel B two days ago; a resumed sync must not treat them alike.
CURSOR_A = NOW - 10 * DAY
CURSOR_B = NOW - 2 * DAY
# Newest message seen by the last sync that read every channel to the end.
LAST_COMPLETE_READ = NOW - 7 * DAY
# New messages (each with one reply) waiting in both channels.
NEW_MESSAGE_A = NOW - 3600
NEW_MESSAGE_B = NOW - 1800


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
    token_config["start_date"] = datetime.fromtimestamp(START_DATE, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    token_config["lookback_window"] = 1
    token_config["channel_filter"] = []
    token_config.update(overrides)
    return token_config


def _channel_messages_state(cursors, read_completely_until=None):
    return {
        **({"state": {"float_ts": f"{read_completely_until}.0"}} if read_completely_until else {}),
        "use_global_cursor": False,
        "states": [
            {"partition": {"channel": channel, "parent_slice": {}}, "cursor": {"float_ts": f"{cursor}.0"}}
            for channel, cursor in cursors.items()
        ],
        "lookback_window": 1,
        "parent_state": {},
    }


def _history_lower_bounds(requests_mock):
    """`oldest` sent to conversations.history, per channel. `latest` is the wall clock, so it is not asserted."""
    bounds = {}
    for request in requests_mock.request_history:
        if "conversations.history" in request.url:
            query = parse_qs(urlparse(request.url).query)
            bounds.setdefault(query["channel"][0], []).append(float(query["oldest"][0]))
    return bounds


def _mock_history_and_replies(requests_mock, messages_by_channel):
    for channel, message_ts in messages_by_channel.items():
        requests_mock.get(
            f"https://slack.com/api/conversations.history?channel={channel}",
            json={"messages": [{"ts": str(message_ts), "thread_ts": str(message_ts), "reply_count": 1}]},
        )
        requests_mock.get(
            f"https://slack.com/api/conversations.replies?channel={channel}&ts={message_ts}",
            json={"messages": [{"ts": str(message_ts)}, {"ts": str(message_ts + 5)}]},
        )


THREADS_CURSORS_SAVED = {
    "use_global_cursor": False,
    "states": [
        {
            "partition": {"float_ts": str(CURSOR_B), "parent_slice": {"channel": "good-reads", "parent_slice": {}}},
            "cursor": {"float_ts": str(CURSOR_B + 5)},
        }
    ],
}


@pytest.mark.parametrize(
    "threads_progress, read_completely_until, expected_lower_bounds",
    (
        pytest.param(
            # Interrupted before threads saved any cursor of its own, e.g. the stream switched to a global
            # cursor past 10k thread partitions, or no thread partition had closed yet.
            {"use_global_cursor": True},
            None,
            {"airbyte-for-beginners": [CURSOR_A - DAY], "good-reads": [CURSOR_B - DAY]},
            id="no_thread_cursors_saved",
        ),
        pytest.param(
            # Threads has its own cursors: the channel that is behind keeps its position, and the channel at the
            # front keeps the extra lookback from the newest thread reply that earlier versions applied.
            THREADS_CURSORS_SAVED,
            None,
            {"airbyte-for-beginners": [CURSOR_A - DAY], "good-reads": [CURSOR_B + 5 - 2 * DAY]},
            id="thread_cursors_saved",
        ),
        pytest.param(
            # An earlier sync read every channel up to LAST_COMPLETE_READ. Channel A has had no message since its
            # cursor, so it continues from that complete read instead of going back to its last message.
            THREADS_CURSORS_SAVED,
            LAST_COMPLETE_READ,
            {"airbyte-for-beginners": [LAST_COMPLETE_READ - DAY], "good-reads": [CURSOR_B + 5 - 2 * DAY]},
            id="thread_cursors_saved_after_a_complete_read",
        ),
    ),
)
def test_threads_resumed_read_continues_each_channel_from_its_saved_cursor(
    requests_mock, token_config, threads_progress, read_completely_until, expected_lower_bounds
):
    config = _config(token_config)
    _mock_history_and_replies(requests_mock, {"airbyte-for-beginners": NEW_MESSAGE_A, "good-reads": NEW_MESSAGE_B})
    saved_state = {
        **threads_progress,
        "lookback_window": 1,
        "parent_state": {
            "channel_messages": _channel_messages_state({"airbyte-for-beginners": CURSOR_A, "good-reads": CURSOR_B}, read_completely_until)
        },
    }
    state = StateBuilder().with_stream_state("threads", saved_state).build()

    output = read(get_source(config, "threads", state), config=config, catalog=_catalog("threads"), state=state)

    assert not output.errors
    assert _history_lower_bounds(requests_mock) == expected_lower_bounds
    assert sorted((record.record.data["channel_id"], record.record.data["ts"]) for record in output.records) == [
        ("airbyte-for-beginners", str(NEW_MESSAGE_A)),
        ("airbyte-for-beginners", str(NEW_MESSAGE_A + 5)),
        ("good-reads", str(NEW_MESSAGE_B)),
        ("good-reads", str(NEW_MESSAGE_B + 5)),
    ]
    emitted_parent_state = output.most_recent_state.stream_state.parent_state["channel_messages"]
    assert {entry["partition"]["channel"]: entry["cursor"]["float_ts"] for entry in emitted_parent_state["states"]} == {
        "airbyte-for-beginners": f"{NEW_MESSAGE_A}.0",
        "good-reads": f"{NEW_MESSAGE_B}.0",
    }


@pytest.mark.parametrize(
    "stream_name, expected_records",
    (
        pytest.param(
            "channel_messages",
            [("archived-member", str(START_DATE + 200)), ("open-joinable", str(START_DATE + 300)), ("open-member", str(START_DATE + 100))],
            id="channel_messages",
        ),
        pytest.param(
            "threads",
            [
                ("archived-member", str(START_DATE + 200)),
                ("archived-member", str(START_DATE + 205)),
                ("open-joinable", str(START_DATE + 300)),
                ("open-joinable", str(START_DATE + 305)),
                ("open-member", str(START_DATE + 100)),
                ("open-member", str(START_DATE + 105)),
            ],
            id="threads",
        ),
    ),
)
def test_archived_channels_the_bot_cannot_join_are_not_requested(requests_mock, token_config, stream_name, expected_records):
    config = _config(token_config, include_archived_channels=True, join_channels=True)
    requests_mock.get(
        "https://slack.com/api/conversations.list?limit=999&types=public_channel&exclude_archived=false",
        json={
            "channels": [
                {"id": "open-member", "name": "open-member", "is_member": True, "is_archived": False},
                {"id": "archived-member", "name": "archived-member", "is_member": True, "is_archived": True},
                {"id": "open-joinable", "name": "open-joinable", "is_member": False, "is_archived": False},
                {"id": "archived-not-member", "name": "archived-not-member", "is_member": False, "is_archived": True},
            ]
        },
    )
    join_request = requests_mock.post("https://slack.com/api/conversations.join", json={"ok": True})
    _mock_history_and_replies(
        requests_mock, {"open-member": START_DATE + 100, "archived-member": START_DATE + 200, "open-joinable": START_DATE + 300}
    )
    # What Slack answers for a channel the bot is not in; the connector ignores it, so the request is pure waste.
    requests_mock.get(
        "https://slack.com/api/conversations.history?channel=archived-not-member", json={"ok": False, "error": "not_in_channel"}
    )

    output = read(get_source(config, stream_name), config=config, catalog=_catalog(stream_name))

    assert not output.errors
    assert sorted(_history_lower_bounds(requests_mock)) == ["archived-member", "open-joinable", "open-member"]
    assert [request.json() for request in join_request.request_history] == [{"channel": "open-joinable"}]
    assert sorted((record.record.data["channel_id"], record.record.data["ts"]) for record in output.records) == expected_records
