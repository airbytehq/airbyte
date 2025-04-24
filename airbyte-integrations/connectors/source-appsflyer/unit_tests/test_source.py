#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest
from source_appsflyer.source import SourceAppsflyer


@pytest.mark.parametrize(
    ("timezone", "http_status", "response_text", "expected_result"),
    [
        ("UTC", HTTPStatus.OK, "", (True, None)),
        ("UTC", HTTPStatus.NOT_FOUND, "", (False, "The supplied APP ID is invalid")),
        ("UTC", HTTPStatus.BAD_REQUEST, "The supplied API token is invalid", (False, "The supplied API token is invalid")),
        ("Invalid", None, "", (False, "The supplied timezone is invalid.")),
    ],
)
def test_check_connection(mocker, timezone, http_status, response_text, expected_result):
    with patch("requests.request") as mock_request:
        mock_request.return_value.status_code = http_status
        mock_request.return_value.text = response_text
        source = SourceAppsflyer()
        config = {
            "app_id": "app.yourapp.android",
            "api_token": "secret",
            "start_date": "2021-09-27 20:00:00",
            "timezone": timezone,
        }
        logger_mock = MagicMock()
        assert source.check_connection(logger_mock, config) == expected_result


def test_streams():
    source = SourceAppsflyer()
    config_mock = {"app_id": "testing", "api_token": "secrets", "start_date": "2021-09-13 01:00:00", "timezone": "UTC"}
    streams = source.streams(config_mock)
    expected_streams_number = 18
    assert len(streams) == expected_streams_number
