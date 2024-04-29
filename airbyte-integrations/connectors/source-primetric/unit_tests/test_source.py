#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging

from source_primetric.source import SourcePrimetric


def mock_response():
    return {"results": ["mock1", "mock2"]}


def test_connection_success(requests_mock, config_pass, assignments_url, auth_url, auth_token):
    requests_mock.post(auth_url, json=auth_token)
    requests_mock.get(url=assignments_url, status_code=200, json=mock_response())
    source = SourcePrimetric()
    status, msg = source.check_connection(logging.getLogger(), config_pass)
    assert (status, msg) == (True, None)


def test_streams(requests_mock, config_pass, assignments_url, auth_url, auth_token):
    source = SourcePrimetric()
    requests_mock.post(auth_url, json=auth_token)
    requests_mock.get(url=assignments_url, status_code=200, json=mock_response())
    streams = source.streams(config_pass)
    expected_streams_number = 21
    assert len(streams) == expected_streams_number
