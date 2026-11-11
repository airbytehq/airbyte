# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
from freezegun import freeze_time

from airbyte_cdk.models import ConfiguredAirbyteCatalogSerializer
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


def read_stream(config, stream_name, stream_state):
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
    state = StateBuilder().with_stream_state(stream_name, stream_state).build()
    return read(get_source(config, stream_name, state), config=config, catalog=catalog, state=state)


@freeze_time("2021-08-01T00:00:00Z")
def test_threads_read_resumes_per_channel_parent_cursors(requests_mock, token_config):
    cursors = {"airbyte-for-beginners": 1627257600.0, "good-reads": 1627430400.0}
    stream_state = {
        "states": [],
        "parent_state": {
            "channel_messages": {
                "states": [
                    {"partition": {"channel": channel, "parent_slice": {}}, "cursor": {"float_ts": str(cursor)}}
                    for channel, cursor in cursors.items()
                ]
            }
        },
    }
    requests_mock.get("https://slack.com/api/conversations.history", json={"ok": True, "messages": []})

    output = read_stream(token_config, "threads", stream_state)

    assert not output.errors
    history = [request for request in requests_mock.request_history if "conversations.history" in request.url]
    assert {request.qs["channel"][0] for request in history} == set(cursors)
    for request in history:
        channel = request.qs["channel"][0]
        assert float(request.qs["oldest"][0]) == cursors[channel] - 86400


@pytest.mark.parametrize("stream_name", ["channel_messages", "threads"])
@freeze_time("2021-08-01T00:00:00Z")
def test_read_skips_archived_non_member_channels(requests_mock, token_config, stream_name):
    token_config.update({"include_archived_channels": True, "join_channels": True, "channel_filter": []})
    requests_mock.get(
        "https://slack.com/api/conversations.list",
        json={
            "ok": True,
            "channels": [
                {"id": "member", "name": "member", "is_member": True, "is_archived": False},
                {"id": "joinable", "name": "joinable", "is_member": False, "is_archived": False},
                {"id": "archived", "name": "archived", "is_member": False, "is_archived": True},
            ],
        },
    )
    join = requests_mock.post("https://slack.com/api/conversations.join", json={"ok": True})
    requests_mock.get("https://slack.com/api/conversations.history", json={"ok": True, "messages": []})

    output = read_stream(token_config, stream_name, {})

    assert not output.errors
    assert {request.json()["channel"] for request in join.request_history} == {"joinable"}
    history = [request for request in requests_mock.request_history if "conversations.history" in request.url]
    assert {request.qs["channel"][0] for request in history} == {"member", "joinable"}
