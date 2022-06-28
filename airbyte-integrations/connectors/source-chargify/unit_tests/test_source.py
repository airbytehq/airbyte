#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_chargify.source import SourceChargify


def test_streams(mocker):
    source = SourceChargify()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 2
    assert len(streams) == expected_streams_number
