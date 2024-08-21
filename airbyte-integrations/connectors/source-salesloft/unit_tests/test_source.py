#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import logging

import pytest
from source_salesloft.source import SourceSalesloft


def mock_response():
    return {"data": [{"id": "mock1"}, {"id": "mock2"}]}


def test_streams(config):
    source = SourceSalesloft()
    streams = source.streams(config)
    expected_streams_number = 29
    assert len(streams) == expected_streams_number


@pytest.mark.parametrize("status_code, check_successful", ((403, False), (200, True)))
def test_check_connection(requests_mock, config, status_code, check_successful):
    requests_mock.post("https://accounts.salesloft.com/oauth/token", json={"access_token": "token", "expires_in": 7200})
    requests_mock.get("https://api.salesloft.com/v2/users", status_code=status_code, json=mock_response())
    source = SourceSalesloft()
    ok, error = source.check_connection(logging.getLogger(), config)
    assert ok is check_successful
    assert bool(error) is not check_successful
