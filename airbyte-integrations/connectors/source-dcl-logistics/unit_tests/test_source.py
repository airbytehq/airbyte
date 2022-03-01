#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import requests
from source_dcl_logistics.source import SourceDclLogistics


def test_check_connection(mocker):
    source = SourceDclLogistics()
    logger_mock, config_mock = MagicMock(), MagicMock()
    mocker.patch.object(requests, "request", return_value=MagicMock(ok=True))
    assert source.check_connection(logger_mock, config_mock) == (True, None)


def test_streams(mocker):
    source = SourceDclLogistics()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 1
    assert len(streams) == expected_streams_number
