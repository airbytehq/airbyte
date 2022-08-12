#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_firestore.source import SourceFirestore


def test_check_connection(mocker):
    source = SourceFirestore()
    logger_mock, config_mock = MagicMock(), MagicMock()

    res, _err = source.check_connection(logger_mock, config_mock)

    assert res is False


def test_streams(mocker):
    source = SourceFirestore()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 1
    assert len(streams) == expected_streams_number
