#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest
from source_qonto.source import SourceQonto


@pytest.mark.parametrize(
    ("http_status", "response_text", "expected_result"),
    [
        (HTTPStatus.OK, "", (True, None)),
        (HTTPStatus.NOT_FOUND, " ", (False, "Not Found, the specified IBAN might be wrong")),
        (
            HTTPStatus.UNAUTHORIZED,
            "Invalid credentials",
            (False, "Invalid credentials, the organization slug or secret key might be wrong"),
        ),
    ],
)
def test_check_connection(mocker, http_status, response_text, expected_result):
    with patch("requests.request") as mock_request:
        mock_request.return_value.status_code = http_status
        mock_request.return_value.text = response_text
        source = SourceQonto()
        logger_mock, config_mock = MagicMock(), MagicMock()
        print(http_status)
        assert source.check_connection(logger_mock, config_mock) == expected_result


def test_streams(mocker):
    source = SourceQonto()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 3
    assert len(streams) == expected_streams_number
