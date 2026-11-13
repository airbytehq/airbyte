# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
from freezegun import freeze_time

from airbyte_cdk.models import ConfiguredAirbyteCatalogSerializer
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


def read_stream(stream_name, config, stream_state):
    state = StateBuilder().with_stream_state(stream_name, stream_state).build()
    catalog = ConfiguredAirbyteCatalogSerializer.load(
        {
            "streams": [
                {
                    "stream": {"name": stream_name, "json_schema": {}, "supported_sync_modes": ["incremental"]},
                    "sync_mode": "incremental",
                    "destination_sync_mode": "append",
                }
            ]
        }
    )
    return read(get_source(config, stream_name, state), config=config, catalog=catalog, state=state)


@freeze_time("2021-07-26T20:00:00Z")
@pytest.mark.parametrize("threads_cursor", [{"state": {"float_ts": "1627243200"}, "use_global_cursor": True}, {"states": []}])
def test_threads_preserves_per_channel_parent_state(requests_mock, token_config, threads_cursor):
    saved_cursors = {"airbyte-for-beginners": 1627156800, "good-reads": 1627243200}
    parent_state = {
        "states": [
            {"partition": {"channel": channel, "parent_slice": {}}, "cursor": {"float_ts": str(cursor)}}
            for channel, cursor in saved_cursors.items()
        ],
        "state": {"float_ts": "1627070400"},
        "use_global_cursor": False,
        "lookback_window": 86400,
    }
    persisted_state = {**threads_cursor, "parent_state": {"channel_messages": parent_state}}
    requests_mock.get("https://slack.com/api/conversations.history", json={"ok": True, "messages": []})

    read_stream("threads", token_config, persisted_state)

    oldest_by_channel = {
        request.qs["channel"][0]: float(request.qs["oldest"][0])
        for request in requests_mock.request_history
        if request.path == "/api/conversations.history"
    }
    assert oldest_by_channel == {channel: cursor - 86400 for channel, cursor in saved_cursors.items()}


@freeze_time("2021-07-26T20:00:00Z")
@pytest.mark.parametrize("stream_name", ["channel_messages", "threads"])
def test_skips_archived_non_member_channels(requests_mock, token_config, stream_name):
    token_config.update({"channel_filter": [], "include_archived_channels": True, "join_channels": True})
    requests_mock.get(
        "https://slack.com/api/conversations.list",
        json={
            "ok": True,
            "channels": [
                {"id": "archived-outsider", "name": "archived-outsider", "is_archived": True, "is_member": False},
                {"id": "archived-member", "name": "archived-member", "is_archived": True, "is_member": True},
                {"id": "active-outsider", "name": "active-outsider", "is_archived": False, "is_member": False},
            ],
        },
    )
    requests_mock.post("https://slack.com/api/conversations.join", json={"ok": True})
    requests_mock.get("https://slack.com/api/conversations.history", json={"ok": True, "messages": []})

    read_stream(stream_name, token_config, {})

    requested_channels = {
        request.qs["channel"][0]
        for request in requests_mock.request_history
        if request.path == "/api/conversations.history"
    }
    assert requested_channels == {"archived-member", "active-outsider"}
