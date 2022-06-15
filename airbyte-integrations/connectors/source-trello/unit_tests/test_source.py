#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_trello.source import SourceTrello


def test_streams(mocker):
    source = SourceTrello()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 6
    assert len(streams) == expected_streams_number
