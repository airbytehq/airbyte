#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies.constant_backoff_strategy import ConstantBackoffStrategy

BACKOFF_TIME = 10
OPTIONS_BACKOFF_TIME = 20
CONFIG_BACKOFF_TIME = 30


@pytest.mark.parametrize(
    "test_name, attempt_count, backofftime, expected_backoff_time",
    [
        ("test_constant_backoff_first_attempt", 1, BACKOFF_TIME, BACKOFF_TIME),
        ("test_constant_backoff_first_attempt_float", 1, 6.7, 6.7),
        ("test_constant_backoff_attempt_round_float", 1.0, 6.7, 6.7),
        ("test_constant_backoff_attempt_round_float", 1.5, 6.7, 6.7),
        ("test_constant_backoff_first_attempt_round_float", 1, 10.0, BACKOFF_TIME),
        ("test_constant_backoff_second_attempt_round_float", 2, 10.0, BACKOFF_TIME),
        ("test_constant_backoff_from_options", 1, "{{ options['backoff'] }}", OPTIONS_BACKOFF_TIME),
        ("test_constant_backoff_from_config", 1, "{{ config['backoff'] }}", CONFIG_BACKOFF_TIME),
    ],
)
def test_constant_backoff(test_name, attempt_count, backofftime, expected_backoff_time):
    response_mock = MagicMock()
    backoff_strategy = ConstantBackoffStrategy(
        options={"backoff": OPTIONS_BACKOFF_TIME}, backoff_time_in_seconds=backofftime, config={"backoff": CONFIG_BACKOFF_TIME}
    )
    backoff = backoff_strategy.backoff(response_mock, attempt_count)
    assert backoff == expected_backoff_time
