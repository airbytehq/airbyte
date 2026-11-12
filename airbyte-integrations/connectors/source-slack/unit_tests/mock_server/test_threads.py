#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import re
from urllib.parse import parse_qs, urlparse

import freezegun
import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder, ConfiguredAirbyteStreamBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


_NOW = "2024-03-01T00:00:00Z"
_NOW_TS = 1709251200.0
_START_DATE_TS = 1704067200.0  # 2024-01-01T00:00:00Z
_LOOKBACK_SECONDS = 7 * 24 * 60 * 60

_HISTORY_URL = re.compile(r"https://slack\.com/api/conversations\.history\?.*")
_REPLIES_URL = re.compile(r"https://slack\.com/api/conversations\.replies\?.*")


@pytest.fixture
def config(token_config):
    token_config.pop("end_date")
    token_config.update({"start_date": "2024-01-01T00:00:00Z", "lookback_window": 7, "join_channels": True, "channel_filter": []})
    return token_config


def _given_channels(requests_mock, channels):
    requests_mock.get(re.compile(r"https://slack\.com/api/conversations\.list\?.*"), json={"ok": True, "channels": channels})


def _given_messages_and_replies(requests_mock):
    def history(request, context):
        channel = _query(request)["channel"]
        return {"ok": True, "messages": [{"ts": f"{_MESSAGE_TS[channel]}", "reply_count": 1, "thread_ts": f"{_MESSAGE_TS[channel]}"}]}

    def replies(request, context):
        return {"ok": True, "messages": [{"ts": _query(request)["ts"]}]}

    requests_mock.get(_HISTORY_URL, json=history)
    requests_mock.get(_REPLIES_URL, json=replies)


_MESSAGE_TS = {"C1": "1709100000.000100", "C2": "1708100000.000200", "C3": "1708200000.000300", "C4": "1708300000.000400"}


def _query(request):
    return {key: values[0] for key, values in parse_qs(urlparse(request.url).query).items()}


def _history_requests(requests_mock):
    return {_query(r)["channel"]: float(_query(r)["oldest"]) for r in requests_mock.request_history if "conversations.history" in r.url}


def _read(config, stream_name, state=None):
    state = StateBuilder().with_stream_state(stream_name, state).build() if state is not None else None
    catalog = (
        CatalogBuilder().with_stream(ConfiguredAirbyteStreamBuilder().with_name(stream_name).with_sync_mode(SyncMode.incremental)).build()
    )
    return read(get_source(config, stream_name, state), config=config, catalog=catalog, state=state)


def _parent_cursors(output):
    parent_state = output.most_recent_state.stream_state.__dict__["parent_state"]["channel_messages"]
    return {s["partition"]["channel"]: float(s["cursor"]["float_ts"]) for s in parent_state["states"]}


@freezegun.freeze_time(_NOW)
@pytest.mark.parametrize(
    "thread_states",
    [
        pytest.param([], id="interrupted_before_any_thread_cursor"),
        pytest.param(
            [
                {
                    "partition": {"float_ts": "1708900000.000100", "parent_slice": {"channel": "C1", "parent_slice": {}}},
                    "cursor": {"float_ts": "1709000000"},
                },
                {
                    "partition": {"float_ts": "1707900000.000200", "parent_slice": {"channel": "C2", "parent_slice": {}}},
                    "cursor": {"float_ts": "1708000000"},
                },
            ],
            id="with_thread_cursors",
        ),
    ],
)
def test_resumed_threads_read_continues_each_channel_from_its_parent_cursor(requests_mock, config, thread_states):
    _given_channels(requests_mock, [{"id": "C1", "name": "c1", "is_member": True}, {"id": "C2", "name": "c2", "is_member": True}])
    _given_messages_and_replies(requests_mock)
    state = {
        "use_global_cursor": False,
        "states": thread_states,
        "lookback_window": 0,
        "parent_state": {
            "channel_messages": {
                "use_global_cursor": False,
                "states": [
                    {"partition": {"channel": "C1", "parent_slice": {}}, "cursor": {"float_ts": "1709000000.0"}},
                    {"partition": {"channel": "C2", "parent_slice": {}}, "cursor": {"float_ts": "1708000000.0"}},
                ],
                "lookback_window": 0,
                "parent_state": {},
            }
        },
    }

    output = _read(config, "threads", state)

    assert not output.errors
    # each channel resumes from its own saved cursor minus the configured lookback window, not from start_date
    assert _history_requests(requests_mock) == {"C1": 1709000000.0 - _LOOKBACK_SECONDS, "C2": 1708000000.0 - _LOOKBACK_SECONDS}
    assert sorted((r.record.data["channel_id"], r.record.data["ts"]) for r in output.records) == [
        ("C1", _MESSAGE_TS["C1"]),
        ("C2", _MESSAGE_TS["C2"]),
    ]
    assert _parent_cursors(output) == {"C1": float(_MESSAGE_TS["C1"]), "C2": float(_MESSAGE_TS["C2"])}


@freezegun.freeze_time(_NOW)
def test_threads_read_with_state_from_previous_read_does_not_restart_from_start_date(requests_mock, config):
    _given_channels(requests_mock, [{"id": "C1", "name": "c1", "is_member": True}, {"id": "C2", "name": "c2", "is_member": True}])
    _given_messages_and_replies(requests_mock)
    first = _read(config, "threads")
    assert _history_requests(requests_mock) == {"C1": _START_DATE_TS, "C2": _START_DATE_TS}
    requests_mock.reset_mock()

    second = _read(config, "threads", first.most_recent_state.stream_state.__dict__)

    assert not second.errors
    assert _history_requests(requests_mock) == {
        "C1": float(_MESSAGE_TS["C1"]) - _LOOKBACK_SECONDS,
        "C2": float(_MESSAGE_TS["C2"]) - _LOOKBACK_SECONDS,
    }
    # lookback overlap: the threads within the lookback window are read again
    assert sorted(r.record.data["ts"] for r in second.records) == sorted([_MESSAGE_TS["C1"], _MESSAGE_TS["C2"]])


@freezegun.freeze_time(_NOW)
@pytest.mark.parametrize("stream_name", ["channel_messages", "threads"])
def test_archived_channels_the_bot_cannot_join_are_not_requested(requests_mock, config, stream_name):
    config["include_archived_channels"] = True
    _given_channels(
        requests_mock,
        [
            {"id": "C1", "name": "c1", "is_member": True, "is_archived": False},
            {"id": "C2", "name": "c2", "is_member": False, "is_archived": False},
            {"id": "C3", "name": "c3", "is_member": False, "is_archived": True},
            {"id": "C4", "name": "c4", "is_member": True, "is_archived": True},
        ],
    )
    requests_mock.post("https://slack.com/api/conversations.join", json={"ok": True})
    _given_messages_and_replies(requests_mock)

    output = _read(config, stream_name)

    assert not output.errors
    # C2 is joinable; C4 is archived but the bot is already a member; C3 is archived and cannot be joined
    assert set(_history_requests(requests_mock)) == {"C1", "C2", "C4"}
    assert not any(_query(r)["channel"] == "C3" for r in requests_mock.request_history if "conversations.replies" in r.url)
    assert sorted(r.record.data["channel_id"] for r in output.records) == ["C1", "C2", "C4"]
