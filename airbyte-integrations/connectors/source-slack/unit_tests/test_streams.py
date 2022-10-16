#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import Mock

import pendulum
import pytest
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from source_slack.source import Threads, Users


@pytest.fixture
def authenticator(legacy_token_config):
    return TokenAuthenticator(legacy_token_config["api_token"])


@pytest.mark.parametrize(
    "start_date, end_date, messages, stream_state, expected_result",
    (
        (
            "2020-01-01T00:00:00Z",
            "2020-01-02T00:00:00Z",
            [{"ts": 1577866844}, {"ts": 1577877406}],
            {},
            [
                # two messages per each channel
                {"channel": 3, "ts": 1577866844},
                {"channel": 3, "ts": 1577877406},
                {"channel": 4, "ts": 1577866844},
                {"channel": 4, "ts": 1577877406},
            ],
        ),
        ("2020-01-02T00:00:00Z", "2020-01-01T00:00:00Z", [], {}, [{}]),
        (
            "2020-01-01T00:00:00Z",
            "2020-01-02T00:00:00Z",
            [{"ts": 1577866844}, {"ts": 1577877406}],
            {"float_ts": 1577915266},
            [
                # two messages per each channel per datetime slice
                {"channel": 3, "ts": 1577866844},
                {"channel": 3, "ts": 1577877406},
                {"channel": 3, "ts": 1577866844},
                {"channel": 3, "ts": 1577877406},
                {"channel": 4, "ts": 1577866844},
                {"channel": 4, "ts": 1577877406},
                {"channel": 4, "ts": 1577866844},
                {"channel": 4, "ts": 1577877406},
            ],
        ),
    ),
)
def test_threads_stream_slices(
    requests_mock, authenticator, legacy_token_config, start_date, end_date, messages, stream_state, expected_result
):
    requests_mock.register_uri(
        "GET", "https://slack.com/api/conversations.history", [{"json": {"messages": messages}}, {"json": {"messages": messages}}]
    )
    start_date = pendulum.parse(start_date)
    end_date = end_date and pendulum.parse(end_date)
    stream = Threads(
        authenticator=authenticator,
        default_start_date=start_date,
        end_date=end_date,
        lookback_window=pendulum.Duration(days=legacy_token_config["lookback_window"]),
        channel_filter=legacy_token_config["channel_filter"],
    )
    slices = list(stream.stream_slices(stream_state=stream_state))
    assert slices == expected_result


@pytest.mark.parametrize(
    "current_state, latest_record, expected_state",
    (
        ({}, {"float_ts": 1507866844}, {"float_ts": 1626984000.0}),
        ({}, {"float_ts": 1726984000}, {"float_ts": 1726984000.0}),
        ({"float_ts": 1588866844}, {"float_ts": 1577866844}, {"float_ts": 1588866844}),
        ({"float_ts": 1577800844}, {"float_ts": 1577866844}, {"float_ts": 1577866844}),
    ),
)
def test_get_updated_state(authenticator, legacy_token_config, current_state, latest_record, expected_state):
    stream = Threads(
        authenticator=authenticator,
        default_start_date=pendulum.parse(legacy_token_config["start_date"]),
        lookback_window=legacy_token_config["lookback_window"],
        channel_filter=legacy_token_config["channel_filter"],
    )
    assert stream.get_updated_state(current_stream_state=current_state, latest_record=latest_record) == expected_state


@pytest.mark.parametrize("headers, expected_result", (({}, 5), ({"Retry-After": 15}, 15)))
def test_backoff(authenticator, headers, expected_result):
    stream = Users(authenticator=authenticator)
    assert stream.backoff_time(Mock(headers=headers)) == expected_result
