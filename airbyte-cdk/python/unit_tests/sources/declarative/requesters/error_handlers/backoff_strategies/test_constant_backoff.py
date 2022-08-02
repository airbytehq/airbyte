#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies.constant_backoff_strategy import ConstantBackoffStrategy

BACKOFF_TIME = 10


@pytest.mark.parametrize(
    "test_name, attempt_count, expected_backoff_time",
    [
        ("test_exponential_backoff", 1, BACKOFF_TIME),
        ("test_exponential_backoff", 2, BACKOFF_TIME),
    ],
)
def test_exponential_backoff(test_name, attempt_count, expected_backoff_time):
    response_mock = MagicMock()
    backoff_strategy = ConstantBackoffStrategy(backoff_time_in_seconds=BACKOFF_TIME)
    backoff = backoff_strategy.backoff(response_mock, attempt_count)
    assert backoff == expected_backoff_time
