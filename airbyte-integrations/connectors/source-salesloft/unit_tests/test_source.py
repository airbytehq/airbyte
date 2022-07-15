#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_salesloft.source import SourceSalesloft


def test_streams(mocker):
    source = SourceSalesloft()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 23
    assert len(streams) == expected_streams_number
