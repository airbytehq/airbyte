#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging

import pytest
import requests
from conftest import TEST_CONFIG, get_source

from airbyte_cdk.models import Status
from airbyte_cdk.sources.streams.http.exceptions import DefaultBackoffException


@pytest.mark.parametrize(
    "exception, expected_error_fragment",
    (
        (
            ConnectionError("Connection aborted"),
            "Connection aborted",
        ),
        (
            TimeoutError("Socket timed out"),
            "Socket timed out",
        ),
        (
            DefaultBackoffException(
                None, None, "Unexpected exception in error handler: 401 Client Error: Unauthorized for url: https://api.twilio.com/"
            ),
            "401 Client Error: Unauthorized",
        ),
    ),
)
def test_check_connection_handles_exceptions(mocker, exception, expected_error_fragment):
    """Test that check connection properly handles network-level exceptions."""
    mocker.patch("time.sleep")
    mocker.patch.object(requests.Session, "send", side_effect=exception)

    source = get_source(TEST_CONFIG)
    logger = logging.getLogger("airbyte")

    connection_status = source.check(logger=logger, config=TEST_CONFIG)

    assert connection_status.status == Status.FAILED
    assert expected_error_fragment in str(connection_status.message)
