#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest
from airbyte_cdk.sources.declarative.requesters.retriers.default_retrier import DefaultRetrier, HttpResponseFilter


@pytest.mark.parametrize(
    "test_name, http_code, response_headers, should_retry, backoff_time",
    [
        # ("test_bad_gateway", HTTPStatus.BAD_GATEWAY, {}, True, 60),
        # ("test_retry_after", HTTPStatus.BAD_GATEWAY, {"Retry-After": 120}, True, 120),
        # ("test_bad_gateway", HTTPStatus.BAD_GATEWAY, {"X-RateLimit-Reset": 1655804724}, True, 300.0),
    ],
)
@patch("time.time", return_value=1655804424.0)
def test_something(time_mock, test_name, http_code, response_headers, should_retry, backoff_time):
    response_mock = MagicMock()
    response_mock.status_code = http_code
    response_mock.headers = response_headers
    retrier = DefaultRetrier()
    assert retrier.should_retry(response_mock) == should_retry
    assert retrier.backoff_time(response_mock) == backoff_time


@pytest.mark.parametrize(
    "test_name, http_code, response_filter, response_headers, should_retry, backoff_time",
    [
        ("test_bad_gateway", HTTPStatus.BAD_GATEWAY, None, {}, True, None),
        ("test_403", HTTPStatus.FORBIDDEN, None, {}, False, None),
        ("test_429", HTTPStatus.TOO_MANY_REQUESTS, None, {}, True, None),
        ("test_403_with_predicate", HTTPStatus.FORBIDDEN, HttpResponseFilter(predicate="{{ 'code' in decoded_response }}"), {}, True, None),
        (
            "test_403_with_predicate",
            HTTPStatus.FORBIDDEN,
            HttpResponseFilter(predicate="{{ 'some_absent_field' in decoded_response }}"),
            {},
            False,
            None,
        ),
        ("test_retry_403", HTTPStatus.FORBIDDEN, HttpResponseFilter([HTTPStatus.FORBIDDEN]), {}, True, None),
    ],
)
@patch("time.time", return_value=1655804424.0)
def test_default_retrier(time_mock, test_name, http_code, response_filter, response_headers, should_retry, backoff_time):
    response_mock = MagicMock()
    response_mock.status_code = http_code
    response_mock.headers = response_headers
    response_mock.json.return_value = {"code": "1000"}
    retrier = DefaultRetrier(response_filter)
    assert retrier.should_retry(response_mock) == should_retry
    assert retrier.backoff_time(response_mock) == backoff_time
