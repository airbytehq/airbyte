#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_klaviyo_custom.source import SourceKlaviyoCustom


def test_check_connection(mocker):
    source = SourceKlaviyoCustom()
    logger_mock, config_mock = MagicMock(), MagicMock()
    mock_response = MagicMock(status_code=200)
    mocker.patch("source_klaviyo_custom.source.requests.get",return_value=mock_response)
    assert source.check_connection(logger_mock, config_mock) == (True, None)


def test_streams(mocker):
    source = SourceKlaviyoCustom()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    # TODO: replace this with your streams number
    expected_streams_number = 3
    assert len(streams) == expected_streams_number
