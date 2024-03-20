#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import pendulum
import pytest
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from airbyte_protocol.models import SyncMode
from freezegun import freeze_time
from source_slack import SourceSlack


@pytest.fixture
def authenticator(legacy_token_config):
    return TokenAuthenticator(legacy_token_config["api_token"])


def get_stream_by_name(stream_name, config):
    streams = SourceSlack().streams(config=config)
    for stream in streams:
        if stream.name == stream_name:
            return stream
    raise ValueError(f"Stream {stream_name} not found")


@freeze_time("2024-03-10T20:00:00Z", tz_offset=-2)
def test_threads_stream_slices(requests_mock, token_config):
    start_date = "2024-03-01T20:00:00Z"
    end_date = pendulum.now()
    oldest, latest = int(pendulum.parse(start_date).timestamp()), int(end_date.timestamp())
    token_config["start_date"] = start_date

    for channel in token_config["channel_filter"]:
        requests_mock.get(
            url=f"https://slack.com/api/conversations.history?"
                f"inclusive=True&limit=1000&channel={channel}&"
                f"oldest={oldest}&latest={latest}",
            json={"messages": [{"ts": latest}, {"ts": oldest}]}
        )

    threads_stream = get_stream_by_name("threads", token_config)
    slices = threads_stream.stream_slices(stream_state=None, sync_mode=SyncMode.full_refresh)

    expected = [{"ts": 1710093600, "channel": "airbyte-for-beginners", "start_time": "1709236800", "end_time": "1710093600"},
                {"ts": 1709323200, "channel": "airbyte-for-beginners", "start_time": "1709236800", "end_time": "1710093600"},
                {"ts": 1710093600, "channel": "good-reads", "start_time": "1709236800", "end_time": "1710093600"},
                {"ts": 1709323200, "channel": "good-reads", "start_time": "1709236800", "end_time": "1710093600"}]

    assert list(slices) == expected
