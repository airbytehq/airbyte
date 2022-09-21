#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies.exponential_backoff_strategy import (
    ExponentialBackoffStrategy,
)


@pytest.mark.parametrize(
    "test_name, attempt_count, expected_backoff_time",
    [
        ("test_exponential_backoff", 1, 10),
        ("test_exponential_backoff", 2, 20),
    ],
)
def test_exponential_backoff(test_name, attempt_count, expected_backoff_time):
    response_mock = MagicMock()
    backoff_strategy = ExponentialBackoffStrategy(factor=5)
    backoff = backoff_strategy.backoff(response_mock, attempt_count)
    assert backoff == expected_backoff_time


def test_exponential_backoff_default():
    response_mock = MagicMock()
    backoff_strategy = ExponentialBackoffStrategy()
    backoff = backoff_strategy.backoff(response_mock, 3)
    assert backoff == 40
