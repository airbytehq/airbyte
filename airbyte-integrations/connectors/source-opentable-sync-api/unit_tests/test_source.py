#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_opentable_sync_api.source import SourceOpentableSyncAPI


def test_check_connection(mocker, config):
    source = SourceOpentableSyncAPI()
    logger_mock = MagicMock()
    assert source.check_connection(logger_mock, config) == (True, None)


def test_streams(mocker, config):
    source = SourceOpentableSyncAPI()
    streams = source.streams(config)
    # TODO: replace this with your streams number
    expected_streams_number = 2
    assert len(streams) == expected_streams_number
