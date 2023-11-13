#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies.exponential_backoff_strategy import (
    ExponentialBackoffStrategy,
)

parameters = {"backoff": 5}
config = {"backoff": 5}


@pytest.mark.parametrize(
    "test_name, attempt_count, factor, expected_backoff_time",
    [
        ("test_exponential_backoff_first_attempt", 1, 5, 10),
        ("test_exponential_backoff_second_attempt", 2, 5, 20),
        ("test_exponential_backoff_from_parameters", 2, "{{parameters['backoff']}}", 20),
        ("test_exponential_backoff_from_config", 2, "{{config['backoff']}}", 20),
    ],
)
def test_exponential_backoff(test_name, attempt_count, factor, expected_backoff_time):
    response_mock = MagicMock()
    backoff_strategy = ExponentialBackoffStrategy(factor=factor, parameters=parameters, config=config)
    backoff = backoff_strategy.backoff(response_mock, attempt_count)
    assert backoff == expected_backoff_time


def test_exponential_backoff_default():
    response_mock = MagicMock()
    backoff_strategy = ExponentialBackoffStrategy(parameters=parameters, config=config)
    backoff = backoff_strategy.backoff(response_mock, 3)
    assert backoff == 40
