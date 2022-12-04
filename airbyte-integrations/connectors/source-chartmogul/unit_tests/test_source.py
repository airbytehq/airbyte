#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from requests.exceptions import HTTPError
from source_chartmogul.source import SourceChartmogul


def test_check_connection(mocker, requests_mock):
    source = SourceChartmogul()
    logger_mock, config_mock = MagicMock(), MagicMock()

    # success
    requests_mock.get("https://api.chartmogul.com/v1/ping", json={"data": "pong!"})
    assert source.check_connection(logger_mock, config_mock) == (True, None)

    # failure
    requests_mock.get("https://api.chartmogul.com/v1/ping", status_code=500)
    ok, err = source.check_connection(logger_mock, config_mock)
    assert (ok, type(err)) == (False, HTTPError)


def test_streams(mocker):
    source = SourceChartmogul()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 3
    assert len(streams) == expected_streams_number
