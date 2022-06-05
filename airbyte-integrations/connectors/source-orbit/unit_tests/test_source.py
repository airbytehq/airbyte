#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_orbit.source import SourceOrbit


def disabled(f):
    def _decorator():
        print(f.__name__ + " has been disabled")

    return _decorator


# TODO: figure out how to properly pass in the config here.
@disabled
def test_check_connection(mocker, config):
    source = SourceOrbit()
    logger_mock = MagicMock()
    assert source.check_connection(logger_mock, config) == (True, None)


def test_streams(mocker):
    source = SourceOrbit()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 2
    assert len(streams) == expected_streams_number
