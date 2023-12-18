#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from airbyte_cdk.sources.streams.http.rate_limiting import default_backoff_handler
from requests import exceptions


def helper_with_exceptions(exception_type):
    raise exception_type


@pytest.mark.parametrize(
    "max_tries, max_time, factor, exception_to_raise",
    [
        (1, None, 1, exceptions.ConnectTimeout),
        (1, 1, 0, exceptions.ReadTimeout),
        (2, 2, 1, exceptions.ConnectionError),
        (3, 3, 1, exceptions.ChunkedEncodingError),
    ],
)
def test_default_backoff_handler(max_tries: int, max_time: int, factor: int, exception_to_raise: Exception):
    backoff_handler = default_backoff_handler(max_tries=max_tries, max_time=max_time, factor=factor)(helper_with_exceptions)
    with pytest.raises(exception_to_raise):
        backoff_handler(exception_to_raise)
