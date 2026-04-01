#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from unittest.mock import MagicMock

import pytest
from requests import Response

from airbyte_cdk.sources.streams.http.error_handlers import ResponseAction
from unit_tests.conftest import get_source


def _get_stream_by_name(stream_name, config):
    source = get_source(config)
    streams = source.streams(config)
    for stream in streams:
        if stream.name == stream_name:
            return stream
    raise ValueError(f"Stream {stream_name} not found")


def _get_retriever(stream):
    return stream._stream_partition_generator._partition_factory._retriever


def test_streams():
    config_mock = {"start_date": "2020-01-01T00:00:00.000Z", "credentials": {"auth_type": "token", "token": "abcd"}}
    source = get_source(config_mock)
    streams = source.streams(config_mock)
    expected_streams_number = 5
    assert len(streams) == expected_streams_number


def test_streams_no_start_date_in_config():
    config_mock = {"credentials": {"auth_type": "token", "token": "abcd"}}
    source = get_source(config_mock)
    streams = source.streams(config_mock)
    expected_streams_number = 5
    assert len(streams) == expected_streams_number


@pytest.mark.parametrize(
    "status_code, expected_action",
    [
        (200, ResponseAction.SUCCESS),
        (429, ResponseAction.RATE_LIMITED),
        (500, ResponseAction.RETRY),
    ],
)
def test_error_handler_maps_429_to_rate_limited(status_code, expected_action):
    """
    Verify that HTTP 429 responses are mapped to RATE_LIMITED (not RETRY).

    Using RATE_LIMITED ensures:
    1. The CDK emits a RATE_LIMITED stream status for observability.
    2. The CDK retries endlessly on rate limits (when exit_on_rate_limit is False),
       preventing syncs from failing after max retries on busy workspaces.
    """
    config = {"start_date": "2020-01-01T00:00:00.000Z", "credentials": {"auth_type": "token", "token": "abcd"}}
    stream = _get_stream_by_name("pages", config)
    retriever = _get_retriever(stream)

    mocked_response = MagicMock(spec=Response, status_code=status_code)
    mocked_response.ok = status_code == 200
    mocked_response.headers = {"Content-Type": "application/json"}

    result = retriever.requester.error_handler.interpret_response(mocked_response)
    assert result.response_action == expected_action
