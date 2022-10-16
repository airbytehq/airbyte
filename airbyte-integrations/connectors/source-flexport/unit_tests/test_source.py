#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import re
from unittest.mock import MagicMock

import pytest
from source_flexport.source import SourceFlexport
from source_flexport.streams import FlexportStream


@pytest.mark.parametrize(
    ("status_code", "response", "expected"),
    [
        (200, {}, (True, None)),
        (401, {}, (False, "401 Client Error")),
        (401, {"errors": [{"code": "server_error", "message": "Server error"}]}, (False, "server_error: Server error")),
    ],
)
def test_check_connection(mocker, requests_mock, status_code, response, expected):
    expected_ok, expected_error = expected
    requests_mock.get(FlexportStream.url_base + "network/companies?page=1&per=1", status_code=status_code, json=response)

    source = SourceFlexport()
    logger_mock, config_mock = MagicMock(), MagicMock()

    ok, error = source.check_connection(logger_mock, config_mock)
    assert ok == expected_ok
    if isinstance(expected_error, str):
        assert re.match(expected_error, str(error))
    else:
        assert error == expected_error


def test_streams(mocker):
    source = SourceFlexport()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 5
    assert len(streams) == expected_streams_number
