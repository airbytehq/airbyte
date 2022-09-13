#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import Mock, MagicMock
import logging

from source_commcare.source import SourceCommcare


def test_check_connection_ok(mocker):
    source = SourceCommcare()
    logger_mock, config_mock = MagicMock(), MagicMock()
    d = {'api-key': 'apikey'}
    config_mock.__getitem__.side_effect = d.__getitem__
    config_mock.__iter__.side_effect = d.__iter__
    config_mock.__contains__.side_effect = d.__contains__
    assert source.check_connection(logger_mock, config_mock) == (True, None)

def test_check_connection_fail(mocker):
    source = SourceCommcare()
    logger_mock, config_mock = MagicMock(), MagicMock()
    assert source.check_connection(logger_mock, config_mock) == (False, None)


def test_streams(mocker):
    source = SourceCommcare()
    config_mock = MagicMock()
    d = {'api-key': 'apikey'}
    config_mock.__getitem__.side_effect = d.__getitem__
    config_mock.__iter__.side_effect = d.__iter__
    config_mock.__contains__.side_effect = d.__contains__
    streams = source.streams(config_mock)
    expected_streams_number = 2
    assert len(streams) == expected_streams_number
