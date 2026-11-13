#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, MutableMapping
from urllib.parse import parse_qs, urlparse

import freezegun
import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder, ConfiguredAirbyteStreamBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


_NOW = "2026-11-13T00:00:00Z"
_NOW_TS = 1794528000.0
_DAY = 86400
_CONVERSATIONS_LIST_URL = "https://slack.com/api/conversations.list"
_HISTORY_URL = "https://slack.com/api/conversations.history"
_REPLIES_URL = "https://slack.com/api/conversations.replies"
_JOIN_URL = "https://slack.com/api/conversations.join"


def _config(**overrides: Any) -> MutableMapping[str, Any]:
    config = {
        "start_date": "2026-01-01T00:00:00Z",
        "lookback_window": 1,
        "join_channels": True,
        "include_archived_channels": True,
        "channel_filter": [],
        "credentials": {"option_title": "API Token Credentials", "api_token": "api-token"},
    }
    config.update(overrides)
    return config


def _read(stream_name: str, config: Mapping[str, Any], stream_state: Mapping[str, Any]):
    catalog = (
        CatalogBuilder().with_stream(ConfiguredAirbyteStreamBuilder().with_name(stream_name).with_sync_mode(SyncMode.incremental)).build()
    )
    state = StateBuilder().with_stream_state(stream_name, stream_state).build()
    return read(get_source(config, stream_name, state), config=config, catalog=catalog, state=state)


def _history_requests(requests_mock) -> List[Mapping[str, List[str]]]:
    return [parse_qs(urlparse(r.url).query) for r in requests_mock.request_history if r.url.startswith(_HISTORY_URL)]


def _channel_messages_parent_state(cursors: Mapping[str, float]) -> Mapping[str, Any]:
    return {
        "use_global_cursor": False,
        "states": [
            {"partition": {"channel": channel, "parent_slice": {}}, "cursor": {"float_ts": str(ts)}} for channel, ts in cursors.items()
        ],
        "lookback_window": 0,
        "parent_state": {},
    }


_C1_CURSOR = _NOW_TS - 1 * _DAY
_C2_CURSOR = _NOW_TS - 5 * _DAY


@pytest.mark.parametrize(
    "thread_states",
    [
        pytest.param([], id="interrupted_before_any_thread_partition_checkpointed"),
        pytest.param(
            [
                {
                    "partition": {"float_ts": str(_C1_CURSOR), "parent_slice": {"channel": "C1", "parent_slice": {}}},
                    "cursor": {"float_ts": str(int(_C1_CURSOR))},
                }
            ],
            id="thread_partitions_checkpointed_for_one_channel",
        ),
    ],
)
@freezegun.freeze_time(_NOW)
def test_threads_resume_reads_each_channel_from_its_saved_parent_cursor(requests_mock, thread_states):
    """
    A threads state that already carries per-channel `channel_messages` cursors must resume each channel from
    its own cursor (minus the lookback window), not from `start_date` nor from a single collapsed cursor.
    """
    requests_mock.get(
        _CONVERSATIONS_LIST_URL,
        json={"channels": [{"id": "C1", "name": "general", "is_member": True}, {"id": "C2", "name": "random", "is_member": True}]},
    )
    requests_mock.get(_HISTORY_URL, json={"messages": []})
    stream_state = {
        "use_global_cursor": False,
        "states": thread_states,
        "lookback_window": 0,
        "parent_state": {"channel_messages": _channel_messages_parent_state({"C1": _C1_CURSOR, "C2": _C2_CURSOR})},
    }

    output = _read("threads", _config(), stream_state)

    assert not output.errors
    oldest_by_channel = {}
    for query in _history_requests(requests_mock):
        oldest_by_channel.setdefault(query["channel"][0], []).append(float(query["oldest"][0]))
    # lookback_window=1 day is applied to each channel's own saved cursor; one request window per channel
    assert oldest_by_channel == {"C1": [_C1_CURSOR - _DAY], "C2": [_C2_CURSOR - _DAY]}


@pytest.mark.parametrize("stream_name", ["channel_messages", "threads"])
@freezegun.freeze_time(_NOW)
def test_archived_channels_bot_cannot_join_are_not_partitioned(requests_mock, stream_name):
    """
    With join_channels and include_archived_channels enabled, archived channels the bot is not a member of
    cannot be joined (Slack rejects conversations.join), so no conversations.history requests must be made for them.
    """
    requests_mock.get(
        _CONVERSATIONS_LIST_URL,
        json={
            "channels": [
                {"id": "C_ACTIVE_MEMBER", "name": "a", "is_member": True, "is_archived": False},
                {"id": "C_ACTIVE_NON_MEMBER", "name": "b", "is_member": False, "is_archived": False},
                {"id": "C_ARCHIVED_MEMBER", "name": "c", "is_member": True, "is_archived": True},
                {"id": "C_ARCHIVED_NON_MEMBER", "name": "d", "is_member": False, "is_archived": True},
            ]
        },
    )
    requests_mock.post(_JOIN_URL, json={"ok": True})
    requests_mock.get(_HISTORY_URL, json={"messages": []})
    config = _config(start_date="2026-11-10T00:00:00Z")

    output = _read(stream_name, config, {})

    assert not output.errors
    requested_channels = sorted({query["channel"][0] for query in _history_requests(requests_mock)})
    assert requested_channels == ["C_ACTIVE_MEMBER", "C_ACTIVE_NON_MEMBER", "C_ARCHIVED_MEMBER"]
