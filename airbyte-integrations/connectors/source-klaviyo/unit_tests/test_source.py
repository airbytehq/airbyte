#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging

import pendulum
import pytest
from source_klaviyo.source import SourceKlaviyo

logger = logging.getLogger("airbyte")


@pytest.mark.parametrize(
    ("status_code", "is_connection_successful", "error_msg"),
    (
        (200, True, None),
        (
            400,
            False,
            "Unable to connect to stream metrics - 400 Client Error: None for url: https://a.klaviyo.com/api/metrics",
        ),
        (
            403,
            False,
            (
                "Unable to read metrics stream. The endpoint https://a.klaviyo.com/api/metrics returned 403: None. "
                "This is most likely due to insufficient permissions on the credentials in use. "
                "Try to grant required permissions/scopes or re-authenticate. "
                "Please visit https://docs.airbyte.com/integrations/sources/klaviyo to learn more.  "
            ),
        ),
    ),
)
def test_check_connection(requests_mock, status_code, is_connection_successful, error_msg):
    requests_mock.register_uri(
        "GET",
        "https://a.klaviyo.com/api/metrics",
        status_code=status_code,
        json={"end": 1, "total": 1} if 200 >= status_code < 300 else {},
    )
    source = SourceKlaviyo()
    success, error = source.check_connection(logger=logger, config={"api_key": "api_key"})
    assert success is is_connection_successful
    assert error == error_msg


def test_check_connection_unexpected_error(requests_mock):
    requests_mock.register_uri("GET", "https://a.klaviyo.com/api/metrics", exc=Exception("Something went wrong"))
    source = SourceKlaviyo()
    success, error = source.check_connection(logger=logger, config={"api_key": "api_key"})
    assert success is False
    assert error == "Unable to connect to stream metrics - Something went wrong"


def test_streams():
    source = SourceKlaviyo()
    config = {"api_key": "some_key", "start_date": pendulum.datetime(2020, 10, 10).isoformat()}
    streams = source.streams(config)
    expected_streams_number = 8
    assert len(streams) == expected_streams_number

    # ensure only unique stream names are returned
    assert len({stream.name for stream in streams}) == expected_streams_number
