#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock, PropertyMock, patch

from source_lexware.source import SourceLexware

# Mock request and response object
ok_response_mock = MagicMock()
type(ok_response_mock).status_code = PropertyMock(return_value=200)


ok_response_mock.json.return_value = "{'blah':'blah'}"


@patch('requests.get', lambda url, headers: ok_response_mock)
def test_check_connection(mocker):
    source = SourceLexware()
    logger_mock, config_mock = MagicMock(), {"apikey": "ABC"}
    assert source.check_connection(logger_mock, config_mock) == (True, None)


def test_streams(mocker):
    source = SourceLexware()
    config_mock = {"apikey": "ABC"}
    streams = source.streams(config_mock)
    # Replace this with your streams number
    expected_streams_number = 1
    assert len(streams) == expected_streams_number
