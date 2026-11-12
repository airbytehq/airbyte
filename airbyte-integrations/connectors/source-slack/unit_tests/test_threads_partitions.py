#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from urllib.parse import parse_qs, urlparse

import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder, ConfiguredAirbyteStreamBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


_START_DATE = "2024-01-01T00:00:00Z"
_START_DATE_TS = 1704067200.0
_CHANNELS = ["airbyte-for-beginners", "good-reads"]


def _threads_catalog():
    return CatalogBuilder().with_stream(ConfiguredAirbyteStreamBuilder().with_name("threads").with_sync_mode(SyncMode.incremental)).build()


def _history_requests(requests_mock):
    """Returns (channel, oldest) for every conversations.history request, in request order."""
    calls = []
    for request in requests_mock.request_history:
        if request.path == "/api/conversations.history":
            query = parse_qs(urlparse(request.url).query)
            calls.append((query["channel"][0], float(query["oldest"][0])))
    return calls


def _message_in_window(request, context):
    """
    airbyte-for-beginners has one message (with a reply) in every date window, so its cursor reaches now.
    good-reads only has a message in its first window, so its cursor stops after that window.
    """
    query = parse_qs(urlparse(request.url).query)
    oldest = float(query["oldest"][0])
    if query["channel"][0] == "good-reads" and oldest != _START_DATE_TS:
        return {"ok": True, "messages": []}
    return {"ok": True, "messages": [{"ts": f"{oldest + 1:.6f}", "reply_count": 1}]}


def _parent_message_ts(request, context):
    return {"ok": True, "messages": [{"ts": parse_qs(urlparse(request.url).query)["ts"][0]}]}


def _as_emitted(state):
    return state


def _threads_switched_to_global_cursor(state):
    """Shape the CDK persists once the threads stream exceeds its per-partition limit: no `states` list."""
    return {
        "use_global_cursor": True,
        "state": state["state"],
        "lookback_window": state["lookback_window"],
        "parent_state": state["parent_state"],
    }


@pytest.mark.parametrize("persisted_state", [_as_emitted, _threads_switched_to_global_cursor])
def test_threads_resumes_each_channel_from_parent_state(requests_mock, token_config, persisted_state):
    """
    A second threads read must resume conversations.history for every channel from that channel's
    own channel_messages cursor emitted by the first read, not from start_date or a single shared value.
    """
    token_config["start_date"] = _START_DATE
    token_config["lookback_window"] = 0
    token_config.pop("end_date")
    requests_mock.get("https://slack.com/api/conversations.history", json=_message_in_window)
    requests_mock.get("https://slack.com/api/conversations.replies", json=_parent_message_ts)

    first_state = StateBuilder().build()
    first = read(get_source(token_config, "threads", first_state), token_config, _threads_catalog(), first_state)
    assert not first.errors
    last_window_start_by_channel = {}
    for channel, oldest in _history_requests(requests_mock):
        last_window_start_by_channel[channel] = max(oldest, last_window_start_by_channel.get(channel, oldest))
    assert set(last_window_start_by_channel) == set(_CHANNELS)

    emitted_state = first.most_recent_state.stream_state.__dict__
    parent_cursor_by_channel = {
        partition_state["partition"]["channel"]: float(partition_state["cursor"]["float_ts"])
        for partition_state in emitted_state["parent_state"]["channel_messages"]["states"]
    }
    # the first read checkpointed each channel at a different point, both past start_date
    assert parent_cursor_by_channel["airbyte-for-beginners"] > last_window_start_by_channel["airbyte-for-beginners"]
    assert parent_cursor_by_channel["airbyte-for-beginners"] > parent_cursor_by_channel["good-reads"] > _START_DATE_TS
    requests_mock.reset_mock()

    second_state = StateBuilder().with_stream_state("threads", persisted_state(emitted_state)).build()
    second = read(get_source(token_config, "threads", second_state), token_config, _threads_catalog(), second_state)
    assert not second.errors

    first_oldest_by_channel = {}
    for channel, oldest in _history_requests(requests_mock):
        first_oldest_by_channel.setdefault(channel, oldest)
    assert first_oldest_by_channel == parent_cursor_by_channel


def test_threads_skips_archived_channels_bot_cannot_join(requests_mock, token_config):
    """
    With join_channels and include_archived_channels enabled, archived channels the bot is not a
    member of cannot be joined, so no message/thread partitions are built for them.
    """
    token_config["channel_filter"] = []
    token_config["include_archived_channels"] = True
    requests_mock.get(
        "https://slack.com/api/conversations.list?limit=999&types=public_channel&exclude_archived=false",
        json={
            "channels": [
                {"id": "C_MEMBER", "name": "member", "is_member": True, "is_archived": False},
                {"id": "C_ARCHIVED_MEMBER", "name": "archived-member", "is_member": True, "is_archived": True},
                {"id": "C_JOINABLE", "name": "joinable", "is_member": False, "is_archived": False},
                {"id": "C_ARCHIVED", "name": "archived", "is_member": False, "is_archived": True},
            ]
        },
    )
    requests_mock.post("https://slack.com/api/conversations.join", json={"ok": True})
    requests_mock.get("https://slack.com/api/conversations.history", json={"ok": True, "messages": []})

    state = StateBuilder().build()
    output = read(get_source(token_config, "threads", state), token_config, _threads_catalog(), state)

    assert not output.errors
    assert {channel for channel, _ in _history_requests(requests_mock)} == {"C_MEMBER", "C_ARCHIVED_MEMBER", "C_JOINABLE"}
    joined = [request.json()["channel"] for request in requests_mock.request_history if request.path == "/api/conversations.join"]
    assert joined == ["C_JOINABLE"]
