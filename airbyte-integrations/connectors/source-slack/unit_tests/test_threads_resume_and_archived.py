#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from urllib.parse import parse_qs, urlparse

import pytest

from airbyte_cdk.test.state_builder import StateBuilder
from airbyte_cdk.utils.datetime_helpers import ab_datetime_parse
from unit_tests.conftest import get_stream_by_name


HISTORY_URL = "https://slack.com/api/conversations.history"
REPLIES_URL = "https://slack.com/api/conversations.replies"
ONE_DAY = 86400


def _history_requests(requests_mock):
    return [parse_qs(urlparse(r.url).query) for r in requests_mock.request_history if r.url.startswith(HISTORY_URL)]


def _first_oldest_per_channel(requests_mock):
    oldest = {}
    for query in _history_requests(requests_mock):
        oldest.setdefault(query["channel"][0], float(query["oldest"][0]))
    return oldest


def _read_partitions(stream):
    return [p.to_slice() for p in stream.generate_partitions()]


@pytest.mark.parametrize("use_global_threads_cursor", [False, True], ids=["per_partition_threads_state", "global_threads_state"])
def test_threads_resumes_from_per_channel_parent_cursors(requests_mock, token_config, use_global_threads_cursor):
    token_config["start_date"] = "2021-01-01T00:00:00Z"
    token_config["lookback_window"] = 1
    beginners_cursor = ab_datetime_parse("2021-06-01T00:00:00Z").timestamp()
    good_reads_cursor = ab_datetime_parse("2021-07-01T00:00:00Z").timestamp()
    threads_cursor = {"float_ts": str(int(good_reads_cursor))}
    threads_state = {
        "use_global_cursor": use_global_threads_cursor,
        "state": threads_cursor,
        "lookback_window": ONE_DAY,
        "parent_state": {
            "channel_messages": {
                "use_global_cursor": False,
                "state": {"float_ts": good_reads_cursor},
                "lookback_window": ONE_DAY,
                "states": [
                    {"partition": {"channel": "airbyte-for-beginners", "parent_slice": {}}, "cursor": {"float_ts": beginners_cursor}},
                    {"partition": {"channel": "good-reads", "parent_slice": {}}, "cursor": {"float_ts": good_reads_cursor}},
                ],
            }
        },
    }
    if not use_global_threads_cursor:
        threads_state["states"] = [
            {
                "partition": {"float_ts": "1622505600.0", "parent_slice": {"channel": "good-reads", "parent_slice": {}}},
                "cursor": threads_cursor,
            }
        ]
    requests_mock.register_uri("GET", HISTORY_URL, json={"messages": []})

    stream = get_stream_by_name("threads", token_config, StateBuilder().with_stream_state("threads", threads_state).build())
    _read_partitions(stream)

    assert _first_oldest_per_channel(requests_mock) == {
        "airbyte-for-beginners": beginners_cursor - ONE_DAY,
        "good-reads": good_reads_cursor - ONE_DAY,
    }


@pytest.mark.parametrize("stream_name", ["channel_messages", "threads"])
def test_archived_non_member_channels_are_not_partitioned_when_joining(requests_mock, token_config, stream_name):
    token_config["channel_filter"] = []
    token_config["include_archived_channels"] = True
    token_config["join_channels"] = True
    requests_mock.register_uri(
        "GET",
        "https://slack.com/api/conversations.list?limit=999&types=public_channel&exclude_archived=false",
        json={
            "channels": [
                {"id": "C_MEMBER", "name": "member", "is_member": True, "is_archived": False},
                {"id": "C_JOINABLE", "name": "joinable", "is_member": False, "is_archived": False},
                {"id": "C_ARCHIVED_MEMBER", "name": "archived-member", "is_member": True, "is_archived": True},
                {"id": "C_ARCHIVED_NON_MEMBER", "name": "archived-non-member", "is_member": False, "is_archived": True},
            ]
        },
    )
    requests_mock.register_uri("POST", "https://slack.com/api/conversations.join", json={"ok": True, "channel": {"name": "joinable"}})
    requests_mock.register_uri("GET", HISTORY_URL, json={"messages": []})

    stream = get_stream_by_name(stream_name, token_config)
    partitions = _read_partitions(stream)

    if stream_name == "channel_messages":
        partitioned_channels = {p["channel"] for p in partitions}
    else:
        partitioned_channels = {q["channel"][0] for q in _history_requests(requests_mock)}
    assert partitioned_channels == {"C_MEMBER", "C_JOINABLE", "C_ARCHIVED_MEMBER"}
