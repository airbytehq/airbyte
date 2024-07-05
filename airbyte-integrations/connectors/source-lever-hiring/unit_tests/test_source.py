#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging

from source_lever_hiring.source import SourceLeverHiring


def mock_response():
    return {"data": ["mock1", "mock2"]}


def test_source(requests_mock, config_pass, users_url, auth_url, auth_token):
    requests_mock.post(auth_url, json=auth_token)
    requests_mock.get(url=users_url, status_code=200, json=mock_response())
    source = SourceLeverHiring()
    status, message = source.check_connection(logging.getLogger(), config_pass)
    streams = source.streams(config_pass)
    assert (status, message) == (True, None)
    assert len(streams) == 7
