#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import re
from typing import Any, List, Mapping, Optional, Tuple

import pytest
import requests_mock as requests_mock_lib
from freezegun import freeze_time

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder, ConfiguredAirbyteStreamBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


_NOW = "2021-01-10T00:00:00Z"
_NOW_TS = 1610236800.0
_START_DATE_TS = 1609459200.0  # 2021-01-01T00:00:00Z
_DAY = 86400.0
_LOOKBACK_DAYS = 1

_C1_CURSOR = 1609804800.0  # 2021-01-05T00:00:00Z
_C2_CURSOR = 1609977600.0  # 2021-01-07T00:00:00Z


def _config(**overrides: Any) -> Mapping[str, Any]:
    config = {
        "start_date": "2021-01-01T00:00:00Z",
        "lookback_window": _LOOKBACK_DAYS,
        "join_channels": True,
        "include_archived_channels": True,
        "channel_filter": [],
        "credentials": {"option_title": "API Token Credentials", "api_token": "api-token"},
    }
    config.update(overrides)
    return config


def _channel_messages_state(c1_cursor: float, c2_cursor: float) -> Mapping[str, Any]:
    return {
        "use_global_cursor": False,
        "lookback_window": 0,
        "parent_state": {},
        "states": [
            {"partition": {"channel": "C1", "parent_slice": {}}, "cursor": {"float_ts": str(c1_cursor)}},
            {"partition": {"channel": "C2", "parent_slice": {}}, "cursor": {"float_ts": str(c2_cursor)}},
        ],
        "state": {"float_ts": str(min(c1_cursor, c2_cursor))},
    }


def _thread_partition_state(channel: str, thread_ts: str, cursor: float) -> Mapping[str, Any]:
    return {
        "partition": {"float_ts": thread_ts, "parent_slice": {"channel": channel, "parent_slice": {}}},
        "cursor": {"float_ts": str(int(cursor))},
    }


def _read(
    stream_name: str,
    config: Mapping[str, Any],
    channels: List[Mapping[str, Any]],
    state: Optional[Mapping[str, Any]] = None,
) -> Tuple[EntrypointOutput, List[Mapping[str, List[str]]]]:
    """Run a real incremental read and return the output plus the query strings sent to conversations.history."""
    with requests_mock_lib.Mocker() as http, freeze_time(_NOW):
        http.get(re.compile(r"https://slack\.com/api/conversations\.list"), json={"channels": channels})
        http.post("https://slack.com/api/conversations.join", json={"ok": True, "channel": {}})
        http.get(
            re.compile(r"https://slack\.com/api/conversations\.history"),
            json={"messages": [{"ts": "1610150400.000100", "thread_ts": "1610150400.000100", "reply_count": 1}]},
        )
        http.get(
            re.compile(r"https://slack\.com/api/conversations\.replies"),
            json={"messages": [{"ts": "1610150400.000100", "thread_ts": "1610150400.000100"}]},
        )
        catalog = CatalogBuilder().with_stream(ConfiguredAirbyteStreamBuilder().with_name(stream_name).with_sync_mode(SyncMode.incremental)).build()
        built_state = StateBuilder().with_stream_state(stream_name, state).build() if state else StateBuilder().build()
        output = read(get_source(config, stream_name, built_state), config=config, catalog=catalog, state=built_state)
        history_queries = [request.qs for request in http.request_history if "conversations.history" in request.url]
    return output, history_queries


_MEMBER_CHANNELS = [
    {"id": "C1", "name": "general", "is_member": True},
    {"id": "C2", "name": "random", "is_member": True},
]


@pytest.mark.parametrize(
    "threads_state",
    [
        pytest.param(
            {
                "use_global_cursor": False,
                "states": [],
                "lookback_window": 0,
                "parent_state": {"channel_messages": _channel_messages_state(_C1_CURSOR, _C2_CURSOR)},
            },
            id="interrupted_before_any_thread_partition_completed",
        ),
        pytest.param(
            {
                "use_global_cursor": False,
                "states": [
                    _thread_partition_state("C1", "1609804800.000100", _C1_CURSOR),
                    _thread_partition_state("C2", "1609977600.000100", _C2_CURSOR),
                ],
                "state": {"float_ts": str(int(_C1_CURSOR))},
                "lookback_window": 0,
                "parent_state": {"channel_messages": _channel_messages_state(_C1_CURSOR, _C2_CURSOR)},
            },
            id="channels_at_different_cursors",
        ),
    ],
)
def test_threads_read_resumes_channel_messages_from_per_channel_parent_state(threads_state):
    """
    A threads state that already carries per-channel `channel_messages` cursors must be resumed as-is:
    each channel's conversations.history request starts at that channel's cursor minus the lookback window,
    instead of all channels restarting from `start_date` or collapsing onto a single shared cursor.
    """
    _, history_queries = _read("threads", _config(), _MEMBER_CHANNELS, state=threads_state)

    oldest_by_channel = {query["channel"][0]: float(query["oldest"][0]) for query in history_queries}
    assert oldest_by_channel == {
        "c1": _C1_CURSOR - _LOOKBACK_DAYS * _DAY,
        "c2": _C2_CURSOR - _LOOKBACK_DAYS * _DAY,
    }
    assert {float(query["latest"][0]) for query in history_queries} == {_NOW_TS}
    assert len(history_queries) == 2


def test_threads_read_with_legacy_state_still_migrates_parent_cursor():
    """Legacy `{"float_ts": ...}` threads state (no parent_state) keeps being migrated into a channel_messages cursor."""
    _, history_queries = _read("threads", _config(), _MEMBER_CHANNELS, state={"float_ts": _C2_CURSOR})

    # The migration subtracts the lookback window once when building the parent cursor, and the
    # channel_messages cursor applies it again on read, so legacy state starts two lookback windows back.
    assert {query["channel"][0]: float(query["oldest"][0]) for query in history_queries} == {
        "c1": _C2_CURSOR - 2 * _LOOKBACK_DAYS * _DAY,
        "c2": _C2_CURSOR - 2 * _LOOKBACK_DAYS * _DAY,
    }


@pytest.mark.parametrize("stream_name", ["channel_messages", "threads"])
def test_archived_channels_the_bot_cannot_join_are_not_partitioned(stream_name):
    """
    With join_channels=true and include_archived_channels=true, only channels the bot can read are partitioned:
    members (archived or not) and joinable non-member channels. Archived non-member channels cannot be joined,
    so no conversations.history request is sent for them.
    """
    channels = [
        {"id": "C1", "name": "member", "is_member": True, "is_archived": False},
        {"id": "C2", "name": "joinable", "is_member": False, "is_archived": False},
        {"id": "C3", "name": "archived-non-member", "is_member": False, "is_archived": True},
        {"id": "C4", "name": "archived-member", "is_member": True, "is_archived": True},
    ]

    output, history_queries = _read(stream_name, _config(), channels)

    assert sorted(query["channel"][0] for query in history_queries) == ["c1", "c2", "c4"]
    assert sorted({record.record.data["channel_id"] for record in output.records}) == ["C1", "C2", "C4"]
    assert output.errors == []
