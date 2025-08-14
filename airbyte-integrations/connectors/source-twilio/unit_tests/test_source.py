#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import Mock

import pytest
import requests
from source_twilio.source import SourceTwilio

from airbyte_cdk.sources.streams.http.exceptions import DefaultBackoffException


@pytest.fixture
def config():
    return {
        "account_sid": "airbyte.io",
        "auth_token": "secret",
        "start_date": "2022-01-01T00:00:00Z",
        "lookback_window": 0,
    }


TEST_INSTANCE = SourceTwilio(config, None, None)


@pytest.mark.parametrize(
    "exception, expected_error_msg",
    (
        (
            ConnectionError("Connection aborted"),
            "Encountered an error while checking availability of stream accounts. Error: Connection aborted",
        ),
        (
            TimeoutError("Socket timed out"),
            "Encountered an error while checking availability of stream accounts. Error: Socket timed out",
        ),
        (
            DefaultBackoffException(
                None, None, "Unexpected exception in error handler: 401 Client Error: Unauthorized for url: https://api.twilio.com/"
            ),
            "Encountered an error while checking availability of stream accounts. "
            "Error: DefaultBackoffException: Unexpected exception in error handler: 401 Client Error: Unauthorized for url: https://api.twilio.com/",
        ),
    ),
)
def test_check_connection_handles_exceptions(mocker, config, exception, expected_error_msg):
    mocker.patch.object(requests.Session, "send", Mock(side_effect=exception))
    logger_mock = Mock()
    status_ok, error = TEST_INSTANCE.check_connection(logger=logger_mock, config=config)
    assert not status_ok
    assert error == expected_error_msg
