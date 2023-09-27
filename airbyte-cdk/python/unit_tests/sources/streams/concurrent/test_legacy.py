#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from unittest.mock import Mock

import pytest
from airbyte_cdk.sources.streams.concurrent.availability_strategy import StreamAvailable, StreamUnavailable
from airbyte_cdk.sources.streams.concurrent.legacy import AvailabilityStrategyFacade


@pytest.mark.parametrize(
    "stream_availability, expected_available, expected_message",
    [
        pytest.param(StreamAvailable(), True, None, id="test_stream_is_available"),
        pytest.param(StreamUnavailable("message"), False, "message", id="test_stream_is_available"),
    ],
)
def test_availability_strategy_facade(stream_availability, expected_available, expected_message):
    strategy = Mock()
    strategy.check_availability.return_value = stream_availability
    facade = AvailabilityStrategyFacade(strategy)

    logger = Mock()
    available, message = facade.check_availability(Mock(), logger, Mock())

    assert available == expected_available
    assert message == expected_message

    strategy.check_availability.assert_called_once_with(logger)
