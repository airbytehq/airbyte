#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
from http import HTTPStatus
from source_appsflyer.source import SourceAppsflyer
from unittest.mock import patch, MagicMock

def test_check_connection_expected_ok():
    with patch("requests.request") as mock_request:
        mock_request.return_value.status_code = 200
        source = SourceAppsflyer()
        logger_mock, config_mock = MagicMock(), MagicMock()
        assert source.check_connection(logger_mock, config_mock) == (True, None)


def test_check_connection_expected_app_id_invalid():
    with patch("requests.request") as mock_request:
        mock_request.return_value.status_code = HTTPStatus.NOT_FOUND
        source = SourceAppsflyer()
        logger_mock, config_mock = MagicMock(), MagicMock()
        assert source.check_connection(logger_mock, config_mock) == (False, "The supplied APP ID is invalid")


def test_check_connection_expected_api_token_invalid():
    with patch("requests.request") as mock_request:
        mock_request.return_value.status_code = HTTPStatus.BAD_REQUEST
        mock_request.return_value.text = "The supplied API token is invalid"
        source = SourceAppsflyer()
        logger_mock, config_mock = MagicMock(), MagicMock()
        assert source.check_connection(logger_mock, config_mock) == (False, "The supplied API token is invalid")


def test_streams():
    source = SourceAppsflyer()
    config_mock = {
        "app_id": "testing",
        "api_token": "secrets",
        "start_date" : "2021-09-13 01:00:00",
        "timezone":"UTC"
    }
    streams = source.streams(config_mock)
    expected_streams_number = 11
    assert len(streams) == expected_streams_number
