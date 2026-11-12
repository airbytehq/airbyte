#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping
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
_ONE_DAY = 86400.0

# Per-channel channel_messages cursors saved under the threads stream's parent_state.
_C1_CURSOR = 1706745600.0  # 2024-02-01
_C2_CURSOR = 1707955200.0  # 2024-02-15

_PARENT_STATE = {
    "channel_messages": {
        "use_global_cursor": False,
        "states": [
            {"partition": {"channel": "C1", "parent_slice": {}}, "cursor": {"float_ts": str(_C1_CURSOR)}},
            {"partition": {"channel": "C2", "parent_slice": {}}, "cursor": {"float_ts": str(_C2_CURSOR)}},
        ],
        "state": {"float_ts": str(_C1_CURSOR)},
        "lookback_window": 0,
        "parent_state": {},
    }
}


def _config(**overrides: Any) -> Mapping[str, Any]:
    config = {
        "start_date": "2024-01-01T00:00:00Z",
        "lookback_window": 1,
        "join_channels": True,
        "include_archived_channels": True,
        "channel_filter": [],
        "credentials": {"option_title": "API Token Credentials", "api_token": "api-token"},
    }
    config.update(overrides)
    return config


def _read(config: Mapping[str, Any], stream_name: str, stream_state: Mapping[str, Any] = None):
    catalog = (
        CatalogBuilder().with_stream(ConfiguredAirbyteStreamBuilder().with_name(stream_name).with_sync_mode(SyncMode.incremental)).build()
    )
    state = StateBuilder().with_stream_state(stream_name, stream_state).build() if stream_state else StateBuilder().build()
    return read(get_source(config, stream_name, state), config=config, catalog=catalog, state=state)


def _history_requests(requests_mock) -> List[Mapping[str, List[str]]]:
    return [parse_qs(urlparse(r.url).query) for r in requests_mock.request_history if urlparse(r.url).path == "/api/conversations.history"]


@pytest.mark.parametrize(
    "threads_state",
    (
        pytest.param(
            # Interrupted sync where threads switched to the global cursor and dropped its per-partition states.
            {"use_global_cursor": True, "states": [], "state": {"float_ts": str(_C2_CURSOR)}, "lookback_window": 0},
            id="threads_global_cursor",
        ),
        pytest.param(
            # Threads per-partition states are ahead of channel C1's message cursor.
            {
                "use_global_cursor": False,
                "states": [
                    {
                        "partition": {"float_ts": "1707955200.000100", "parent_slice": {"channel": "C2", "parent_slice": {}}},
                        "cursor": {"float_ts": str(int(_C2_CURSOR))},
                    }
                ],
                "state": {"float_ts": str(int(_C2_CURSOR))},
                "lookback_window": 0,
            },
            id="threads_per_partition",
        ),
    ),
)
def test_threads_resumes_each_channel_from_its_saved_parent_cursor(requests_mock, threads_state):
    requests_mock.get(
        "https://slack.com/api/conversations.list",
        json={"ok": True, "channels": [{"id": "C1", "name": "c1", "is_member": True}, {"id": "C2", "name": "c2", "is_member": True}]},
    )
    requests_mock.get("https://slack.com/api/conversations.history", json={"ok": True, "messages": []})

    with freezegun.freeze_time(_NOW):
        output = _read(_config(), "threads", {**threads_state, "parent_state": _PARENT_STATE})

    assert not output.errors
    # Each channel resumes from its own saved cursor minus the 1-day lookback window, not from start_date.
    assert sorted((q["channel"][0], float(q["oldest"][0]), float(q["latest"][0])) for q in _history_requests(requests_mock)) == [
        ("C1", _C1_CURSOR - _ONE_DAY, _NOW_TS),
        ("C2", _C2_CURSOR - _ONE_DAY, _NOW_TS),
    ]
    # The per-channel parent cursors survive into the emitted state.
    emitted_parent = output.most_recent_state.stream_state.__dict__["parent_state"]["channel_messages"]
    assert {s["partition"]["channel"]: float(s["cursor"]["float_ts"]) for s in emitted_parent["states"]} == {
        "C1": _C1_CURSOR,
        "C2": _C2_CURSOR,
    }


@pytest.mark.parametrize("stream_name", ("channel_messages", "threads"))
def test_archived_channels_the_bot_cannot_join_are_not_read(requests_mock, stream_name):
    requests_mock.get(
        "https://slack.com/api/conversations.list",
        json={
            "ok": True,
            "channels": [
                {"id": "C1", "name": "member", "is_member": True, "is_archived": False},
                {"id": "C2", "name": "joinable", "is_member": False, "is_archived": False},
                {"id": "C3", "name": "archived-non-member", "is_member": False, "is_archived": True},
                {"id": "C4", "name": "archived-member", "is_member": True, "is_archived": True},
            ],
        },
    )
    join = requests_mock.post("https://slack.com/api/conversations.join", json={"ok": True})
    requests_mock.get("https://slack.com/api/conversations.history", json={"ok": True, "messages": []})

    with freezegun.freeze_time(_NOW):
        output = _read(_config(), stream_name)

    assert not output.errors
    assert sorted(q["channel"][0] for q in _history_requests(requests_mock)) == ["C1", "C2", "C4"]
    assert [r.json() for r in join.request_history] == [{"channel": "C2"}]
