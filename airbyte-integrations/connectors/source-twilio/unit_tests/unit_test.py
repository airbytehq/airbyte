#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import Mock

import pytest
import requests
from source_twilio.source import SourceTwilio


@pytest.fixture
def config():
    return {"account_sid": "airbyte.io", "auth_token": "secret", "start_date": "2022-01-01T00:00:00Z"}


@pytest.mark.parametrize(
    "exception, expected_error_msg",
    (
        (
            ConnectionError("Connection aborted"),
            "Unable to connect to Twilio API with the provided credentials - ConnectionError('Connection aborted')",
        ),
        (
            TimeoutError("Socket timed out"),
            "Unable to connect to Twilio API with the provided credentials - TimeoutError('Socket timed out')",
        ),
        (
            requests.exceptions.HTTPError("401 Client Error: Unauthorized for url: https://api.twilio.com/"),
            "Unable to connect to Twilio API with the provided credentials - "
            "HTTPError('401 Client Error: Unauthorized for url: https://api.twilio.com/')",
        ),
    ),
)
def test_check_connection_handles_exceptions(mocker, config, exception, expected_error_msg):
    mocker.patch.object(requests.Session, "send", Mock(side_effect=exception))
    source = SourceTwilio()
    status_ok, error = source.check_connection(logger=None, config=config)
    assert not status_ok
    assert error == expected_error_msg
