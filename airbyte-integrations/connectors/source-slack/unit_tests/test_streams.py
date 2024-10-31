#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock, Mock

import pendulum
import pytest
from airbyte_cdk.sources.streams.http.error_handlers import ResponseAction
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from requests import Response
from source_slack import SourceSlack
from source_slack.streams import Channels, JoinChannelsStream, Threads


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
        "GET", "https://slack.com/api/conversations.history?limit=1000&channel=airbyte-for-beginners",
        [{"json": {"messages": messages}}, {"json": {"messages": []}}]
    )
    requests_mock.register_uri(
        "GET", "https://slack.com/api/conversations.history?limit=1000&channel=good-reads",
        [{"json": {"messages": messages}}, {"json": {"messages": []}}]
    )

    start_date = pendulum.parse(start_date)
    end_date = end_date and pendulum.parse(end_date)

    stream = Threads(
        authenticator=authenticator,
        default_start_date=start_date,
        end_date=end_date,
        lookback_window=pendulum.Duration(days=token_config["lookback_window"])
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

    stream = Threads(
        authenticator=authenticator,
        default_start_date=pendulum.parse(token_config["start_date"]),
        lookback_window=token_config["lookback_window"]
    )
    assert stream._get_updated_state(current_stream_state=current_state, latest_record=latest_record) == expected_state


def test_threads_request_params(authenticator, token_config):
    stream = Threads(
        authenticator=authenticator,
        default_start_date=pendulum.parse(token_config["start_date"]),
        lookback_window=token_config["lookback_window"]
    )
    threads_slice = {'channel': 'airbyte-for-beginners', 'ts': 1577866844}
    expected = {'channel': 'airbyte-for-beginners', 'limit': 1000, 'ts': 1577866844}
    assert stream.request_params(stream_slice=threads_slice, stream_state={}) == expected


def test_threads_parse_response(mocker, authenticator, token_config):
    stream = Threads(
        authenticator=authenticator,
        default_start_date=pendulum.parse(token_config["start_date"]),
        lookback_window=token_config["lookback_window"]
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


@pytest.mark.parametrize("headers, expected_result", (({}, 5), ({"Retry-After": 15}, 15)))
def test_backoff(token_config, authenticator, headers, expected_result):
    stream = Threads(
        authenticator=authenticator,
        default_start_date=pendulum.parse(token_config["start_date"]),
        lookback_window=token_config["lookback_window"]
    )
    mocked_response = MagicMock(spec=Response, headers=headers)
    assert stream.get_backoff_strategy().backoff_time(mocked_response) == expected_result


def test_channels_stream_with_autojoin(authenticator) -> None:
    """
    The test uses the `conversations_list` fixture(autouse=true) as API mocker.
    """
    expected = [
        {'id': 'airbyte-for-beginners', 'is_member': True},
        {'id': 'good-reads', 'is_member': True}
    ]
    stream = Channels(channel_filter=[], join_channels=True, authenticator=authenticator)
    assert list(stream.read_records(None)) == expected


def test_next_page_token(authenticator, token_config):
    stream = Threads(
        authenticator=authenticator,
        default_start_date=pendulum.parse(token_config["start_date"]),
        lookback_window=token_config["lookback_window"]
    )
    mocked_response = Mock()
    mocked_response.json.return_value = {"response_metadata": {"next_cursor": "next page"}}
    assert stream.next_page_token(mocked_response) == {"cursor": "next page"}


@pytest.mark.parametrize(
    "status_code, expected",
    (
        (200, ResponseAction.SUCCESS),
        (403, ResponseAction.FAIL),
        (429, ResponseAction.RATE_LIMITED),
        (500, ResponseAction.RETRY),
    ),
)
def test_should_retry(authenticator, token_config, status_code, expected):
    stream = Threads(
        authenticator=authenticator,
        default_start_date=pendulum.parse(token_config["start_date"]),
        lookback_window=token_config["lookback_window"]
    )
    mocked_response = MagicMock(spec=Response, status_code=status_code)
    mocked_response.ok = status_code == 200
    assert stream.get_error_handler().interpret_response(mocked_response).response_action == expected

def test_channels_stream_with_include_private_channels_false(authenticator) -> None:
    stream = Channels(channel_filter=[], include_private_channels=False, authenticator=authenticator)

    params = stream.request_params(stream_slice={}, stream_state={})

    assert params.get("types") == 'public_channel'

def test_channels_stream_with_include_private_channels(authenticator) -> None:
    stream = Channels(channel_filter=[], include_private_channels=True, authenticator=authenticator)

    params = stream.request_params(stream_slice={}, stream_state={})

    assert params.get("types") == 'public_channel,private_channel'
