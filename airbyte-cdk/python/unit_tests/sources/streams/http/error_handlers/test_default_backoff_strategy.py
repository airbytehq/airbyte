# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from typing import Optional, Union

import requests
from airbyte_cdk.sources.streams.http.error_handlers import BackoffStrategy, DefaultBackoffStrategy


def test_given_no_arguments_default_backoff_strategy_returns_default_values():
    response = requests.Response()
    backoff_strategy = DefaultBackoffStrategy()
    assert backoff_strategy.max_retries == 5
    assert backoff_strategy.max_time == 600
    assert backoff_strategy.backoff_time(response) is None


class CustomBackoffStrategy(BackoffStrategy):

    def __init__(self, max_retries: int = 5, max_time: int = 60 * 10):
        self.max_retries = max_retries
        self.max_time = max_time

    def backoff_time(self, response_or_exception: Optional[Union[requests.Response, requests.RequestException]]) -> Optional[float]:
        return response_or_exception.headers["Retry-After"]


def test_given_valid_arguments_default_backoff_strategy_returns_values():

    response = requests.Response()
    response.headers["Retry-After"] = 123
    backoff_strategy = CustomBackoffStrategy()
    assert backoff_strategy.max_retries == 5
    assert backoff_strategy.max_time == 600
    assert backoff_strategy.backoff_time(response) == 123
