# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import requests
from airbyte_cdk.sources.streams.http.error_handlers import DefaultBackoffStrategy

def test_given_no_arguments_default_backoff_strategy_returns_default_values():
    response = requests.Response()
    backoff_strategy = DefaultBackoffStrategy()
    assert backoff_strategy.max_retries == 5
    assert backoff_strategy.max_time == 600
    assert backoff_strategy.retry_factor == 5
    assert backoff_strategy.backoff_time(response) == None

def test_given_valid_arguments_default_backoff_strategy_returns_values():

    def backoff_time(response: requests.Response):
        return response.headers.get("Retry-After", 10)

    response = requests.Response()
    response.headers["Retry-After"] = 123
    backoff_strategy = DefaultBackoffStrategy(max_retries=10, max_time=1000, retry_factor=10, backoff_time=backoff_time)
    assert backoff_strategy.max_retries == 10
    assert backoff_strategy.max_time == 1000
    assert backoff_strategy.retry_factor == 10
    assert backoff_strategy.backoff_time(response) == 123
