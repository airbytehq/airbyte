#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_dockerhub.source import SourceDockerhub


def test_check_connection():
    source = SourceDockerhub()
    logger_mock, config_mock = MagicMock(), {
        "docker_username": "airbyte"
    }  # shouldnt actually ping network request in test but we will skip for now
    assert source.check_connection(logger_mock, config_mock) == (True, None)


def test_streams():
    source = SourceDockerhub()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 1
    assert len(streams) == expected_streams_number
