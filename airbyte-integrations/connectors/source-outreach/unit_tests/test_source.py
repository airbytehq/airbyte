#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_outreach.source import SourceOutreach


def test_streams(mocker):
    source = SourceOutreach()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 15
    assert len(streams) == expected_streams_number
