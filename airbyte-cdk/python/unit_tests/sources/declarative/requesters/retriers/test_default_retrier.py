#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import pytest
import requests
from airbyte_cdk.sources.declarative.requesters.retriers.default_retrier import (
    ConstantBackoff,
    DefaultRetrier,
    HttpResponseFilter,
    NonRetriableBehavior,
)


@pytest.mark.parametrize(
    "test_name, status_code, body, backoff, should_retry",
    [
        ("test_ignore", 404, "", None, NonRetriableBehavior.Ignore),
        ("test_fail", 400, "", None, NonRetriableBehavior.Fail),
        ("test_retry_none", 429, "", None, None),
        ("test_retry_constant_backoff", 500, "", ConstantBackoff(5), 5),
        ("test_retry_constant_backoff_cascade", 500, "", [ConstantBackoff(None), ConstantBackoff(5)], 5),
    ],
)
def test_retrier(test_name, status_code, body, backoff, should_retry):
    retrier = DefaultRetrier(ignore=[HttpResponseFilter(http_codes=404)], backoff=backoff)
    response = requests.Response()
    response.status_code = status_code
    assert retrier.should_retry(response) == should_retry
