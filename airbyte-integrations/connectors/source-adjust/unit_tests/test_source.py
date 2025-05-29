#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
import logging

from source_adjust.source import SourceAdjust


def mock_response():
    return {"rows": [{"mock1": "value1", "mock2": "value2"}]}


def test_check_connection(requests_mock, config_pass, report_url, auth_token):
    requests_mock.get(url=report_url, status_code=200, json=mock_response())
    source = SourceAdjust()
    status, message = source.check_connection(logging.getLogger(), config_pass)
    assert (status, message) == (True, None)


def test_streams(config_pass):
    source = SourceAdjust()
    streams = source.streams(config_pass)
    expected_streams_number = 1
    assert len(streams) == expected_streams_number
