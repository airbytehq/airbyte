#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping

import freezegun
import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


_NOW = "2026-10-15T00:00:00Z"
_NOW_TS = 1792022400
_LOOKBACK_SECONDS = 7 * 24 * 60 * 60
_CHANNEL_CURSORS = {"airbyte-for-beginners": 1790000000.0001, "good-reads": 1791000000.0}


def _config(token_config: Mapping[str, Any]) -> Mapping[str, Any]:
    config = dict(token_config)
    config.pop("end_date")
    config.update({"start_date": "2021-07-01T00:00:00Z", "lookback_window": 7, "channel_filter": []})
    return config


def _catalog(stream_name: str):
    return CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()


def _history_requests(requests_mock) -> List[Mapping[str, List[str]]]:
    return [request.qs for request in requests_mock.request_history if request.path == "/api/conversations.history"]


def _parent_state() -> Mapping[str, Any]:
    return {
        "channel_messages": {
            "use_global_cursor": False,
            "states": [
                {"partition": {"channel": channel, "parent_slice": {}}, "cursor": {"float_ts": str(cursor)}}
                for channel, cursor in _CHANNEL_CURSORS.items()
            ],
            "state": {"float_ts": str(max(_CHANNEL_CURSORS.values()))},
            "lookback_window": _LOOKBACK_SECONDS,
        }
    }


@pytest.mark.parametrize(
    "threads_state",
    [
        pytest.param(
            {
                "use_global_cursor": False,
                "states": [
                    {
                        "partition": {"float_ts": "1789000000.0001", "parent_slice": {"channel": "good-reads", "parent_slice": {}}},
                        "cursor": {"float_ts": "1789000000"},
                    }
                ],
                "state": {"float_ts": "1789000000"},
                "lookback_window": _LOOKBACK_SECONDS,
                "parent_state": _parent_state(),
            },
            id="per_partition_threads_state",
        ),
        pytest.param(
            {
                "use_global_cursor": True,
                "state": {"float_ts": "1789000000"},
                "lookback_window": _LOOKBACK_SECONDS,
                "parent_state": _parent_state(),
            },
            id="global_threads_state",
        ),
    ],
)
@freezegun.freeze_time(_NOW)
def test_threads_resumes_each_channel_from_saved_parent_state(requests_mock, token_config, threads_state):
    config = _config(token_config)
    requests_mock.register_uri("GET", "https://slack.com/api/conversations.history", json={"messages": []})
    state = StateBuilder().with_stream_state("threads", threads_state).build()

    read(get_source(config, "threads", state), config=config, catalog=_catalog("threads"), state=state)

    oldest_by_channel = {request["channel"][0]: float(request["oldest"][0]) for request in _history_requests(requests_mock)}
    assert oldest_by_channel == pytest.approx({channel: cursor - _LOOKBACK_SECONDS for channel, cursor in _CHANNEL_CURSORS.items()})
    assert len(_history_requests(requests_mock)) == len(_CHANNEL_CURSORS)


@freezegun.freeze_time(_NOW)
def test_threads_legacy_global_state_without_parent_state_does_not_restart_from_start_date(requests_mock, token_config):
    config = _config(token_config)
    requests_mock.register_uri("GET", "https://slack.com/api/conversations.history", json={"messages": []})
    state = StateBuilder().with_stream_state("threads", {"use_global_cursor": True, "state": {"float_ts": "1789000000"}}).build()

    read(get_source(config, "threads", state), config=config, catalog=_catalog("threads"), state=state)

    # The migration derives the parent cursor from the threads cursor minus the lookback window,
    # and the channel_messages cursor applies its own lookback window on top of that.
    expected_oldest = 1789000000 - 2 * _LOOKBACK_SECONDS
    assert [float(request["oldest"][0]) for request in _history_requests(requests_mock)] == [expected_oldest, expected_oldest]


@pytest.mark.parametrize("stream_name", ["channel_messages", "threads"])
@freezegun.freeze_time(_NOW)
def test_archived_non_member_channels_are_not_partitioned_when_join_channels_enabled(requests_mock, token_config, stream_name):
    config = _config(token_config)
    config.update({"join_channels": True, "include_archived_channels": True, "start_date": "2026-10-01T00:00:00Z"})
    requests_mock.register_uri(
        "GET",
        "https://slack.com/api/conversations.list?limit=999&types=public_channel&exclude_archived=false",
        json={
            "channels": [
                {"id": "C_ACTIVE", "name": "active", "is_member": False, "is_archived": False},
                {"id": "C_ARCHIVED_MEMBER", "name": "archived-member", "is_member": True, "is_archived": True},
                {"id": "C_ARCHIVED", "name": "archived", "is_member": False, "is_archived": True},
            ]
        },
    )
    requests_mock.register_uri("POST", "https://slack.com/api/conversations.join", json={"ok": True})
    requests_mock.register_uri("GET", "https://slack.com/api/conversations.history", json={"messages": []})

    read(get_source(config, stream_name), config=config, catalog=_catalog(stream_name))

    assert sorted(request["channel"][0] for request in _history_requests(requests_mock)) == ["c_active", "c_archived_member"]
