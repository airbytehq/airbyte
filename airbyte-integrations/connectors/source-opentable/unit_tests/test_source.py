#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from datetime import datetime

from unittest.mock import MagicMock

from source_opentable.source import SourceOpentable

def test_check_connection(mocker, config):
    source = SourceOpentable()
    logger_mock = MagicMock()
    assert source.check_connection(logger_mock, config) == (True, None)


def test_streams(mocker, config):
    source = SourceOpentable()
    streams = source.streams(config)
    # TODO: replace this with your streams number
    expected_streams_number = 2
    assert len(streams) == expected_streams_number
