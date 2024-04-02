#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import pendulum
import pytest
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from source_slack import SourceSlack
from source_slack.streams import Threads


@pytest.fixture
def authenticator(token_config):
    return TokenAuthenticator(token_config["credentials"]["api_token"])


def get_stream_by_name(stream_name, config):
    streams = SourceSlack().streams(config=config)
    for stream in streams:
        if stream.name == stream_name:
            return stream
    raise ValueError(f"Stream {stream_name} not found")


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
                {'channel': 'airbyte-for-beginners', 'ts': 1577866844},
                {'channel': 'airbyte-for-beginners', 'ts': 1577877406},
                {'channel': 'good-reads', 'ts': 1577866844},
                {'channel': 'good-reads', 'ts': 1577877406},
            ],
        ),
        ("2020-01-02T00:00:00Z", "2020-01-01T00:00:00Z", [], {}, [{}]),
        (
            "2020-01-01T00:00:00Z",
            "2020-01-02T00:00:00Z",
            [{"ts": 1577866844}, {"ts": 1577877406}],
            {"float_ts": 2577866844},
            [
                # no slice when state greater than ts
                {},
            ],
        ),
    ),
)
def test_threads_stream_slices(
    requests_mock, authenticator, token_config, start_date, end_date, messages, stream_state, expected_result
):
    token_config["channel_filter"] = []

    requests_mock.register_uri(
        "GET", "https://slack.com/api/conversations.history?inclusive=True&limit=1000&channel=airbyte-for-beginners",
        [{"json": {"messages": messages}}, {"json": {"messages": []}}]
    )
    requests_mock.register_uri(
        "GET", "https://slack.com/api/conversations.history?inclusive=True&limit=1000&channel=good-reads",
        [{"json": {"messages": messages}}, {"json": {"messages": []}}]
    )

    start_date = pendulum.parse(start_date)
    end_date = end_date and pendulum.parse(end_date)

    channel_messages_stream = get_stream_by_name("channel_messages", token_config)

    stream = Threads(
        authenticator=authenticator,
        default_start_date=start_date,
        end_date=end_date,
        lookback_window=pendulum.Duration(days=token_config["lookback_window"]),
        parent_stream=channel_messages_stream
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
def test_get_updated_state(authenticator, token_config, current_state, latest_record, expected_state):
    channel_messages_stream = get_stream_by_name("channel_messages", token_config)
    stream = Threads(
        authenticator=authenticator,
        default_start_date=pendulum.parse(token_config["start_date"]),
        lookback_window=token_config["lookback_window"],
        parent_stream=channel_messages_stream
    )
    assert stream.get_updated_state(current_stream_state=current_state, latest_record=latest_record) == expected_state


def test_threads_request_params(authenticator, token_config):
    channel_messages_stream = get_stream_by_name("channel_messages", token_config)
    stream = Threads(
        authenticator=authenticator,
        default_start_date=pendulum.parse(token_config["start_date"]),
        lookback_window=token_config["lookback_window"],
        parent_stream=channel_messages_stream
    )
    threads_slice = {'channel': 'airbyte-for-beginners', 'ts': 1577866844}
    expected = {'channel': 'airbyte-for-beginners', 'limit': 1000, 'ts': 1577866844}
    assert stream.request_params(stream_slice=threads_slice, stream_state={}) == expected


def test_threads_parse_response(mocker, authenticator, token_config):
    channel_messages_stream = get_stream_by_name("channel_messages", token_config)
    stream = Threads(
        authenticator=authenticator,
        default_start_date=pendulum.parse(token_config["start_date"]),
        lookback_window=token_config["lookback_window"],
        parent_stream=channel_messages_stream
    )
    resp = {
        "messages": [
            {
                "type": "message",
                "user": "U061F7AUR",
                "text": "island",
                "thread_ts": "1482960137.003543",
                "reply_count": 3,
                "subscribed": True,
                "last_read": "1484678597.521003",
                "unread_count": 0,
                "ts": "1482960137.003543"
            }
        ]
    }
    resp_mock = mocker.Mock()
    resp_mock.json.return_value = resp
    threads_slice = {'channel': 'airbyte-for-beginners', 'ts': 1577866844}
    actual_response = list(stream.parse_response(response=resp_mock,stream_slice=threads_slice))
    assert len(actual_response) == 1
    assert actual_response[0]["float_ts"] == 1482960137.003543
    assert actual_response[0]["channel_id"] == "airbyte-for-beginners"


