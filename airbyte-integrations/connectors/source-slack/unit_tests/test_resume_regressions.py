# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from datetime import datetime, timezone

import pytest
from freezegun import freeze_time

from airbyte_cdk.test.catalog_builder import CatalogBuilder, ConfiguredAirbyteStreamBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


def read_stream(config, stream_name, stream_state):
    state = StateBuilder().with_stream_state(stream_name, stream_state).build()
    catalog = CatalogBuilder().with_stream(ConfiguredAirbyteStreamBuilder().with_name(stream_name)).build()
    return read(get_source(config, stream_name, state), config=config, catalog=catalog, state=state)


@freeze_time("2021-08-02T20:00:00Z")
def test_threads_resume_uses_per_channel_parent_state(token_config, requests_mock):
    token_config.update(channel_filter=[], lookback_window=7)
    cursor = datetime(2021, 7, 31, 20, tzinfo=timezone.utc).timestamp()
    channels = ["airbyte-for-beginners", "good-reads"]
    parent_state = {
        "states": [{"partition": {"channel": channel, "parent_slice": {}}, "cursor": {"float_ts": str(cursor)}} for channel in channels]
    }
    requests_mock.get("https://slack.com/api/conversations.history", json={"ok": True, "messages": []})

    read_stream(token_config, "threads", {"parent_state": {"channel_messages": parent_state}})

    history = [request for request in requests_mock.request_history if request.path.endswith("conversations.history")]
    assert {request.qs["channel"][0] for request in history} == set(channels)
    assert {float(request.qs["oldest"][0]) for request in history} == {cursor - 7 * 86400}


@pytest.mark.parametrize("stream_name", ["channel_messages", "threads"])
@freeze_time("2021-07-23T20:00:00Z")
def test_archived_non_member_has_no_message_partitions(token_config, requests_mock, stream_name):
    token_config.update(channel_filter=[], include_archived_channels=True, join_channels=True)
    requests_mock.get(
        "https://slack.com/api/conversations.list",
        json={"ok": True, "channels": [{"id": "archived", "name": "archived", "is_archived": True, "is_member": False}]},
    )
    requests_mock.get("https://slack.com/api/conversations.history", json={"ok": True, "messages": []})

    read_stream(token_config, stream_name, {})

    history = [request for request in requests_mock.request_history if request.path.endswith("conversations.history")]
    assert history == []
