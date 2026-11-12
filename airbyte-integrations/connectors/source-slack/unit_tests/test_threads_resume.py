#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from urllib.parse import parse_qs, urlparse

import freezegun

from airbyte_cdk.models import SyncMode

from airbyte_cdk.test.catalog_builder import CatalogBuilder, ConfiguredAirbyteStreamBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


_CHANNELS = ["airbyte-for-beginners", "good-reads"]
_SAVED_CHANNEL_CURSORS = {"airbyte-for-beginners": "1628121600.0", "good-reads": "1628208000.0"}  # 2021-08-05, 2021-08-06
_ONE_DAY = 86400


def _catalog(stream_name):
    return CatalogBuilder().with_stream(ConfiguredAirbyteStreamBuilder().with_name(stream_name).with_sync_mode(SyncMode.incremental)).build()


def _history_requests(requests_mock):
    return [r for r in requests_mock.request_history if r.path == "/api/conversations.history"]


@freezegun.freeze_time("2021-08-10T00:00:00Z")
def test_threads_resume_uses_saved_per_channel_parent_state(requests_mock, token_config):
    token_config.pop("end_date")
    requests_mock.get("https://slack.com/api/conversations.history", json={"ok": True, "messages": []})
    threads_state = {
        "use_global_cursor": False,
        "states": [],
        "lookback_window": 0,
        "parent_state": {
            "channel_messages": {
                "use_global_cursor": False,
                "states": [
                    {"partition": {"channel": channel, "parent_slice": {}}, "cursor": {"float_ts": cursor}}
                    for channel, cursor in _SAVED_CHANNEL_CURSORS.items()
                ],
                "state": {"float_ts": "1628121600.0"},
                "lookback_window": 0,
            }
        },
    }
    state = StateBuilder().with_stream_state("threads", threads_state).build()
    source = get_source(token_config, "threads", state)

    output = read(source, config=token_config, catalog=_catalog("threads"), state=state)

    assert not output.errors
    oldest_by_channel = {}
    for request in _history_requests(requests_mock):
        query = parse_qs(urlparse(request.url).query)
        oldest_by_channel.setdefault(query["channel"][0], []).append(float(query["oldest"][0]))
    assert set(oldest_by_channel) == set(_CHANNELS)
    for channel, cursor in _SAVED_CHANNEL_CURSORS.items():
        # channel_messages applies its own lookback_window (1 day in token_config) to the saved per-channel cursor
        assert min(oldest_by_channel[channel]) == float(cursor) - _ONE_DAY


def test_archived_non_member_channels_are_not_partitioned_for_messages(requests_mock, token_config):
    token_config["include_archived_channels"] = True
    token_config["channel_filter"] = []
    requests_mock.get(
        "https://slack.com/api/conversations.list?limit=999&types=public_channel&exclude_archived=false",
        json={
            "channels": [
                {"id": "C_MEMBER", "name": "member", "is_member": True},
                {"id": "C_ARCHIVED_MEMBER", "name": "archived-member", "is_member": True, "is_archived": True},
                {"id": "C_ARCHIVED", "name": "archived", "is_member": False, "is_archived": True},
            ]
        },
    )
    requests_mock.get("https://slack.com/api/conversations.history", json={"ok": True, "messages": []})
    join = requests_mock.post("https://slack.com/api/conversations.join", json={"ok": True, "channel": {}})
    state = StateBuilder().build()
    source = get_source(token_config, "channel_messages", state)

    output = read(source, config=token_config, catalog=_catalog("channel_messages"), state=state)

    assert not output.errors
    requested_channels = {parse_qs(urlparse(r.url).query)["channel"][0] for r in _history_requests(requests_mock)}
    assert requested_channels == {"C_MEMBER", "C_ARCHIVED_MEMBER"}
    assert join.call_count == 0
