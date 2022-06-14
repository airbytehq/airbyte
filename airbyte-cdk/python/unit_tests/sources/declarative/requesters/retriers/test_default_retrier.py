#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import pytest
import requests
from airbyte_cdk.sources.declarative.requesters.retriers.default_retrier import DefaultRetrier, HttpResponseFilter, NonRetriableBehavior


@pytest.mark.parametrize(
    "test_name, status_code, body, should_retry",
    [
        ("test_ignore", 404, "", NonRetriableBehavior.Ignore),
        ("test_ignore", 400, "", NonRetriableBehavior.Fail),
        ("test_ignore", 429, "", None),
        ("test_ignore", 500, "", None),
    ],
)
def test_retrier(test_name, status_code, body, should_retry):
    retrier = DefaultRetrier(ignore=[HttpResponseFilter(http_codes=404)])
    response = requests.Response()
    response.status_code = status_code
    assert retrier.should_retry(response) == should_retry
