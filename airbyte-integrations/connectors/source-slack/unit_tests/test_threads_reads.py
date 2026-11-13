# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from urllib.parse import parse_qs, urlparse

import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder, ConfiguredAirbyteStreamBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


HISTORY_URL = "https://slack.com/api/conversations.history"
REPLIES_URL = "https://slack.com/api/conversations.replies"
START_DATE_TS = 1626984000.0  # 2021-07-22T20:00:00Z
DAY = 86400


def _catalog(stream_name: str):
    return (
        CatalogBuilder().with_stream(ConfiguredAirbyteStreamBuilder().with_name(stream_name).with_sync_mode(SyncMode.incremental)).build()
    )


def _history_requests(requests_mock):
    requests = []
    for request in requests_mock.request_history:
        if request.url.startswith(HISTORY_URL):
            query = parse_qs(urlparse(request.url).query)
            requests.append((query["channel"][0], float(query["oldest"][0])))
    return requests


def test_threads_resumes_from_per_channel_parent_state(token_config, requests_mock):
    config = {**token_config, "end_date": "2021-08-30T00:00:00Z"}
    requests_mock.get(HISTORY_URL, json={"ok": True, "messages": [], "has_more": False})
    requests_mock.get(REPLIES_URL, json={"ok": True, "messages": [], "has_more": False})
    beginners_cursor = START_DATE_TS + 20 * DAY
    good_reads_cursor = START_DATE_TS + 30 * DAY
    state = (
        StateBuilder()
        .with_stream_state(
            "threads",
            {
                "states": [],
                "use_global_cursor": False,
                "state": {"float_ts": str(int(START_DATE_TS + 25 * DAY))},
                "lookback_window": 0,
                "parent_state": {
                    "channel_messages": {
                        "states": [
                            {
                                "partition": {"channel": "airbyte-for-beginners", "parent_slice": {}},
                                "cursor": {"float_ts": beginners_cursor},
                            },
                            {"partition": {"channel": "good-reads", "parent_slice": {}}, "cursor": {"float_ts": good_reads_cursor}},
                        ],
                        "state": {"float_ts": beginners_cursor},
                        "lookback_window": 0,
                        "use_global_cursor": False,
                    }
                },
            },
        )
        .build()
    )

    output = read(get_source(config, "threads", state), config, _catalog("threads"), state)

    assert not output.errors
    first_oldest_per_channel = {}
    for channel, oldest in _history_requests(requests_mock):
        first_oldest_per_channel.setdefault(channel, oldest)
    # channel_messages applies its own 1 day lookback to each per-channel cursor
    assert first_oldest_per_channel == {
        "airbyte-for-beginners": beginners_cursor - DAY,
        "good-reads": good_reads_cursor - DAY,
    }


@pytest.mark.parametrize("stream_name", ["channel_messages", "threads"])
def test_archived_non_member_channels_are_not_partitioned(token_config, requests_mock, stream_name):
    config = {**token_config, "include_archived_channels": True, "join_channels": True}
    config.pop("channel_filter")
    channels = [
        {"id": "C_ACTIVE", "name": "active", "is_member": False, "is_archived": False},
        {"id": "C_ARCHIVED_MEMBER", "name": "archived-member", "is_member": True, "is_archived": True},
        {"id": "C_ARCHIVED", "name": "archived", "is_member": False, "is_archived": True},
    ]
    requests_mock.get("https://slack.com/api/conversations.list", json={"ok": True, "channels": channels})
    join_request = requests_mock.post("https://slack.com/api/conversations.join", json={"ok": True, "channel": {}})
    requests_mock.get(HISTORY_URL, json={"ok": True, "messages": [], "has_more": False})

    output = read(get_source(config, stream_name), config, _catalog(stream_name))

    assert not output.errors
    assert {channel for channel, _ in _history_requests(requests_mock)} == {"C_ACTIVE", "C_ARCHIVED_MEMBER"}
    assert join_request.call_count == 1
