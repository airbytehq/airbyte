#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from urllib.parse import parse_qs, urlparse

import pytest

from airbyte_cdk.models import ConfiguredAirbyteCatalogSerializer
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


ONE_DAY = 86400.0
# Per-channel `channel_messages` cursors saved under the threads `parent_state`. They differ per channel on purpose.
BEGINNERS_CURSOR = 1700000000.0
GOOD_READS_CURSOR = 1710000000.0
PARENT_STATE = {
    "channel_messages": {
        "use_global_cursor": False,
        "states": [
            {"partition": {"channel": "airbyte-for-beginners", "parent_slice": {}}, "cursor": {"float_ts": str(BEGINNERS_CURSOR)}},
            {"partition": {"channel": "good-reads", "parent_slice": {}}, "cursor": {"float_ts": str(GOOD_READS_CURSOR)}},
        ],
        "state": {"float_ts": str(GOOD_READS_CURSOR)},
        "lookback_window": 1,
        "parent_state": {},
    }
}


def _catalog(stream_name: str):
    return ConfiguredAirbyteCatalogSerializer.load(
        {
            "streams": [
                {
                    "stream": {"name": stream_name, "json_schema": {}, "supported_sync_modes": ["full_refresh", "incremental"]},
                    "sync_mode": "incremental",
                    "destination_sync_mode": "append",
                }
            ]
        }
    )


def _history_requests(requests_mock):
    return [parse_qs(urlparse(r.url).query) for r in requests_mock.request_history if "conversations.history" in r.url]


@pytest.mark.parametrize(
    "threads_state",
    (
        pytest.param(
            {
                "use_global_cursor": False,
                "states": [
                    {
                        "partition": {"float_ts": "1700000000.0", "parent_slice": {"channel": "airbyte-for-beginners", "parent_slice": {}}},
                        "cursor": {"float_ts": "1700000000"},
                    }
                ],
                "state": {"float_ts": "1700000000"},
                "lookback_window": 1,
                "parent_state": PARENT_STATE,
            },
            id="per_partition_threads_state",
        ),
        pytest.param(
            # Once the threads stream has too many partitions the CDK switches to a global cursor and stops writing `states`.
            {
                "use_global_cursor": True,
                "state": {"float_ts": "1700000000"},
                "lookback_window": 1,
                "parent_state": PARENT_STATE,
            },
            id="global_cursor_threads_state",
        ),
    ),
)
def test_threads_resume_reads_each_channel_from_its_saved_parent_cursor(requests_mock, token_config, threads_state):
    token_config["channel_filter"] = []
    requests_mock.register_uri("GET", "https://slack.com/api/conversations.history", json={"messages": []})

    state = StateBuilder().with_stream_state("threads", threads_state).build()
    output = read(get_source(token_config, "threads", state), config=token_config, catalog=_catalog("threads"), state=state)

    assert not output.errors
    first_oldest_by_channel = {}
    for query in _history_requests(requests_mock):
        first_oldest_by_channel.setdefault(query["channel"][0], float(query["oldest"][0]))
    # Each channel resumes from its own saved cursor minus the configured 1 day lookback, not from start_date
    # and not from a single value shared by every channel.
    assert first_oldest_by_channel == {
        "airbyte-for-beginners": BEGINNERS_CURSOR - ONE_DAY,
        "good-reads": GOOD_READS_CURSOR - ONE_DAY,
    }


@pytest.mark.parametrize("stream_name", ("channel_messages", "threads"))
def test_archived_non_member_channels_are_not_read_when_joining(requests_mock, token_config, stream_name):
    token_config.update({"channel_filter": [], "join_channels": True, "include_archived_channels": True})
    requests_mock.register_uri(
        "GET",
        "https://slack.com/api/conversations.list?limit=999&types=public_channel&exclude_archived=false",
        json={
            "channels": [
                {"id": "C_MEMBER", "name": "member", "is_member": True, "is_archived": False},
                {"id": "C_JOINABLE", "name": "joinable", "is_member": False, "is_archived": False},
                {"id": "C_ARCHIVED_MEMBER", "name": "archived-member", "is_member": True, "is_archived": True},
                {"id": "C_ARCHIVED", "name": "archived", "is_member": False, "is_archived": True},
            ]
        },
    )
    join = requests_mock.register_uri("POST", "https://slack.com/api/conversations.join", json={"ok": True, "channel": {}})
    requests_mock.register_uri("GET", "https://slack.com/api/conversations.history", json={"messages": []})

    state = StateBuilder().build()
    output = read(get_source(token_config, stream_name, state), config=token_config, catalog=_catalog(stream_name), state=state)

    assert not output.errors
    assert {q["channel"][0] for q in _history_requests(requests_mock)} == {"C_MEMBER", "C_JOINABLE", "C_ARCHIVED_MEMBER"}
    assert [r.json() for r in join.request_history] == [{"channel": "C_JOINABLE"}]
