#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import re
from datetime import datetime, timedelta, timezone
from typing import Any, List, Mapping, MutableMapping
from urllib.parse import parse_qs, urlparse

import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder, ConfiguredAirbyteStreamBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


_NOW = datetime.now(timezone.utc).replace(microsecond=0)
_START_DATE = _NOW - timedelta(days=30)
_LOOKBACK_DAYS = 7
_HISTORY_URL = re.compile(r"https://slack\.com/api/conversations\.history.*")
_REPLIES_URL = re.compile(r"https://slack\.com/api/conversations\.replies.*")
_CHANNELS_URL = re.compile(r"https://slack\.com/api/conversations\.list.*")


def _config(token_config: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
    token_config["start_date"] = _START_DATE.strftime("%Y-%m-%dT%H:%M:%SZ")
    token_config.pop("end_date", None)
    token_config["lookback_window"] = _LOOKBACK_DAYS
    token_config["join_channels"] = True
    token_config["include_archived_channels"] = True
    token_config["channel_filter"] = []
    return token_config


def _read_threads(config: Mapping[str, Any], state: List[Any]) -> EntrypointOutput:
    catalog = (
        CatalogBuilder().with_stream(ConfiguredAirbyteStreamBuilder().with_name("threads").with_sync_mode(SyncMode.incremental)).build()
    )
    return read(get_source(config, "threads", state), config, catalog, state)


def _history_requests(requests_mock) -> Mapping[str, Mapping[str, List[str]]]:
    requests = {}
    for request in requests_mock.request_history:
        if "conversations.history" in request.url:
            query = parse_qs(urlparse(request.url).query)
            requests.setdefault(query["channel"][0], query)
    return requests


def _mock_channels(requests_mock, channels: List[Mapping[str, Any]]) -> None:
    requests_mock.get(_CHANNELS_URL, json={"ok": True, "channels": channels})


def _mock_empty_history_and_replies(requests_mock) -> None:
    requests_mock.get(_HISTORY_URL, json={"ok": True, "messages": []})
    requests_mock.get(_REPLIES_URL, json={"ok": True, "messages": []})


@pytest.mark.parametrize(
    "threads_partition_states",
    [
        pytest.param([], id="interrupted_before_any_thread_checkpoint"),
        pytest.param(
            [
                {
                    "partition": {"float_ts": "1700000000.000100", "parent_slice": {"channel": "C_GENERAL", "parent_slice": {}}},
                    "cursor": {"float_ts": str(int(_START_DATE.timestamp()))},
                }
            ],
            id="with_thread_checkpoints",
        ),
    ],
)
def test_threads_resumes_parent_messages_from_per_channel_cursor(requests_mock, token_config, threads_partition_states):
    """
    A threads state that already carries per-channel channel_messages cursors under parent_state
    must resume conversations.history from each channel's own cursor (minus the lookback window),
    not restart from start_date.
    """
    config = _config(token_config)
    _mock_channels(
        requests_mock,
        [
            {"id": "C_GENERAL", "name": "general", "is_member": True, "is_archived": False},
            {"id": "C_RANDOM", "name": "random", "is_member": True, "is_archived": False},
        ],
    )
    _mock_empty_history_and_replies(requests_mock)

    general_cursor = (_NOW - timedelta(days=2)).timestamp()
    random_cursor = (_NOW - timedelta(days=3)).timestamp()
    state = (
        StateBuilder()
        .with_stream_state(
            "threads",
            {
                "use_global_cursor": False,
                "states": threads_partition_states,
                "lookback_window": 0,
                "parent_state": {
                    "channel_messages": {
                        "use_global_cursor": False,
                        "states": [
                            {"partition": {"channel": "C_GENERAL", "parent_slice": {}}, "cursor": {"float_ts": str(general_cursor)}},
                            {"partition": {"channel": "C_RANDOM", "parent_slice": {}}, "cursor": {"float_ts": str(random_cursor)}},
                        ],
                        "lookback_window": 0,
                    }
                },
            },
        )
        .build()
    )

    output = _read_threads(config, state)

    assert not output.errors
    history = _history_requests(requests_mock)
    assert set(history) == {"C_GENERAL", "C_RANDOM"}
    lookback = timedelta(days=_LOOKBACK_DAYS).total_seconds()
    assert float(history["C_GENERAL"]["oldest"][0]) == pytest.approx(general_cursor - lookback, abs=1)
    assert float(history["C_RANDOM"]["oldest"][0]) == pytest.approx(random_cursor - lookback, abs=1)
    # the persisted per-channel parent cursors survive into the emitted state
    emitted_parent = output.most_recent_state.stream_state.__dict__["parent_state"]["channel_messages"]
    assert {s["partition"]["channel"] for s in emitted_parent["states"]} == {"C_GENERAL", "C_RANDOM"}


def test_threads_legacy_state_without_parent_state_is_still_migrated(requests_mock, token_config):
    """Legacy threads state (single float_ts, no parent_state) is still migrated so channels resume from that cursor, not start_date."""
    config = _config(token_config)
    _mock_channels(requests_mock, [{"id": "C_GENERAL", "name": "general", "is_member": True, "is_archived": False}])
    _mock_empty_history_and_replies(requests_mock)
    legacy_cursor = int((_NOW - timedelta(days=4)).timestamp())

    output = _read_threads(config, StateBuilder().with_stream_state("threads", {"float_ts": legacy_cursor}).build())

    assert not output.errors
    history = _history_requests(requests_mock)
    lookback = timedelta(days=_LOOKBACK_DAYS).total_seconds()
    oldest = float(history["C_GENERAL"]["oldest"][0])
    # resumes from the legacy cursor (with lookback applied), not from start_date
    assert _START_DATE.timestamp() < oldest <= legacy_cursor - lookback


@pytest.mark.parametrize("stream_name", ["channel_messages", "threads"])
def test_archived_channels_bot_cannot_join_are_not_partitioned(requests_mock, token_config, stream_name):
    """
    With join_channels and include_archived_channels enabled, archived channels the bot is not a member of
    cannot be joined, so channel_messages/threads must not request conversations.history for them.
    Archived channels the bot is already a member of are still read.
    """
    config = _config(token_config)
    _mock_channels(
        requests_mock,
        [
            {"id": "C_ACTIVE", "name": "active", "is_member": False, "is_archived": False},
            {"id": "C_ARCHIVED_MEMBER", "name": "archived-member", "is_member": True, "is_archived": True},
            {"id": "C_ARCHIVED_NON_MEMBER", "name": "archived-non-member", "is_member": False, "is_archived": True},
        ],
    )
    requests_mock.post("https://slack.com/api/conversations.join", json={"ok": True})
    message_ts = (_NOW - timedelta(days=1)).timestamp()
    requests_mock.get(
        _HISTORY_URL,
        json={"ok": True, "messages": [{"ts": str(message_ts), "thread_ts": str(message_ts), "reply_count": 1}]},
    )
    requests_mock.get(_REPLIES_URL, json={"ok": True, "messages": [{"ts": str(message_ts), "thread_ts": str(message_ts)}]})

    catalog = (
        CatalogBuilder().with_stream(ConfiguredAirbyteStreamBuilder().with_name(stream_name).with_sync_mode(SyncMode.incremental)).build()
    )
    output = read(get_source(config, stream_name, None), config, catalog, StateBuilder().build())

    assert not output.errors
    assert set(_history_requests(requests_mock)) == {"C_ACTIVE", "C_ARCHIVED_MEMBER"}
    assert {record.record.data["channel_id"] for record in output.records} == {"C_ACTIVE", "C_ARCHIVED_MEMBER"}
