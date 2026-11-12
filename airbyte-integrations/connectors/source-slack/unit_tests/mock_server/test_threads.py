#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import re
from typing import Any, List, Mapping, Optional
from urllib.parse import parse_qs, urlparse

import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder, ConfiguredAirbyteStreamBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


_CONVERSATIONS_LIST = re.compile(r"https://slack\.com/api/conversations\.list.*")
_CONVERSATIONS_HISTORY = re.compile(r"https://slack\.com/api/conversations\.history.*")
_CONVERSATIONS_REPLIES = re.compile(r"https://slack\.com/api/conversations\.replies.*")
_CONVERSATIONS_JOIN = "https://slack.com/api/conversations.join"

_ONE_DAY = 86400.0


def _config(**overrides: Any) -> Mapping[str, Any]:
    config = {
        "credentials": {"option_title": "API Token Credentials", "api_token": "api-token"},
        "start_date": "2021-01-01T00:00:00Z",
        "lookback_window": 1,
        "join_channels": True,
        "include_archived_channels": True,
        "channel_filter": [],
    }
    config.update(overrides)
    return config


def _read(requests_mock, stream_name: str, config: Mapping[str, Any], channels: List[Mapping[str, Any]], state: Optional[Mapping] = None):
    requests_mock.get(_CONVERSATIONS_LIST, json={"ok": True, "channels": channels})
    requests_mock.post(_CONVERSATIONS_JOIN, json={"ok": True, "channel": {}})
    requests_mock.get(_CONVERSATIONS_HISTORY, json={"ok": True, "messages": []})
    requests_mock.get(_CONVERSATIONS_REPLIES, json={"ok": True, "messages": []})
    catalog = (
        CatalogBuilder().with_stream(ConfiguredAirbyteStreamBuilder().with_name(stream_name).with_sync_mode(SyncMode.incremental)).build()
    )
    airbyte_state = StateBuilder().with_stream_state(stream_name, state).build() if state else []
    output = read(get_source(config, stream_name, airbyte_state), config, catalog, airbyte_state)
    # parse the raw URL: requests_mock's `.qs` lowercases values, and Slack channel ids are upper case
    history_requests = [parse_qs(urlparse(r.url).query) for r in requests_mock.request_history if _CONVERSATIONS_HISTORY.match(r.url)]
    return output, history_requests


def _channel_messages_state(cursors: Mapping[str, float]) -> Mapping[str, Any]:
    return {
        "use_global_cursor": False,
        "states": [
            {"partition": {"channel": channel, "parent_slice": {}}, "cursor": {"float_ts": str(cursor)}}
            for channel, cursor in cursors.items()
        ],
        "state": {"float_ts": str(min(cursors.values()))},
        "lookback_window": 1,
        "parent_state": {},
    }


_C1_CURSOR = 1700000000.0
_C2_CURSOR = 1690000000.0


@pytest.mark.parametrize(
    "threads_state",
    [
        pytest.param(
            # sync interrupted before any thread partition completed: only parent cursors were checkpointed
            {
                "use_global_cursor": False,
                "states": [],
                "lookback_window": 1,
                "parent_state": {"channel_messages": _channel_messages_state({"C1": _C1_CURSOR, "C2": _C2_CURSOR})},
            },
            id="parent_state_only",
        ),
        pytest.param(
            {
                "use_global_cursor": False,
                "states": [
                    {
                        "partition": {"float_ts": "1699999000.0001", "parent_slice": {"channel": "C1", "parent_slice": {}}},
                        "cursor": {"float_ts": "1700000000"},
                    },
                ],
                "state": {"float_ts": "1700000000"},
                "lookback_window": 1,
                "parent_state": {"channel_messages": _channel_messages_state({"C1": _C1_CURSOR, "C2": _C2_CURSOR})},
            },
            id="parent_and_thread_states",
        ),
    ],
)
def test_threads_resumes_each_channel_from_its_saved_parent_cursor(requests_mock, threads_state):
    channels = [{"id": "C1", "name": "c1", "is_member": True}, {"id": "C2", "name": "c2", "is_member": True}]

    _, history_requests = _read(requests_mock, "threads", _config(), channels, threads_state)

    # first conversations.history window per channel starts at that channel's saved cursor minus the 1-day lookback,
    # not at start_date and not at a single cursor shared by all channels
    first_oldest = {}
    for params in history_requests:
        channel, oldest = params["channel"][0], float(params["oldest"][0])
        first_oldest[channel] = min(first_oldest.get(channel, oldest), oldest)
    assert first_oldest == {"C1": _C1_CURSOR - _ONE_DAY, "C2": _C2_CURSOR - _ONE_DAY}


@pytest.mark.parametrize("stream_name", ["channel_messages", "threads"])
def test_archived_channels_the_bot_cannot_join_are_not_read(requests_mock, stream_name):
    channels = [
        {"id": "CMEMBER", "name": "member", "is_member": True, "is_archived": False},
        {"id": "CJOINABLE", "name": "joinable", "is_member": False, "is_archived": False},
        {"id": "CARCHIVEDMEMBER", "name": "archived-member", "is_member": True, "is_archived": True},
        {"id": "CARCHIVED", "name": "archived", "is_member": False, "is_archived": True},
    ]

    _, history_requests = _read(requests_mock, stream_name, _config(), channels)

    assert {params["channel"][0] for params in history_requests} == {"CMEMBER", "CJOINABLE", "CARCHIVEDMEMBER"}
