#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
from source_orbit.source import SourceOrbit, Workspace


@pytest.mark.parametrize(
    "read_records_side_effect, expected_return_value, expected_error_message",
    [
        (iter(["foo", "bar"]), True, None),
        (
            Exception("connection error"),
            False,
            "Please check that your API key and workspace name are entered correctly: Exception('connection error')",
        ),
    ],
)
def test_check_connection(mocker, read_records_side_effect, expected_return_value, expected_error_message):
    source = SourceOrbit()
    if expected_error_message:
        read_records_mock = mocker.Mock(side_effect=read_records_side_effect)
    else:
        read_records_mock = mocker.Mock(return_value=read_records_side_effect)
    mocker.patch.object(Workspace, "read_records", read_records_mock)
    logger_mock, config_mock = MagicMock(), MagicMock()
    assert source.check_connection(logger_mock, config_mock) == (expected_return_value, expected_error_message)


def test_streams(mocker):
    source = SourceOrbit()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 2
    assert len(streams) == expected_streams_number
