#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_weatherstack.source import SourceWeatherstack


def test_streams(mocker):
    source = SourceWeatherstack()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 4
    assert len(streams) == expected_streams_number
