#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import Mock

import pytest
from airbyte_cdk.sources.streams.concurrent.adapters import AvailabilityStrategyFacade, StreamFacade
from airbyte_cdk.sources.streams.concurrent.availability_strategy import STREAM_AVAILABLE, StreamAvailable, StreamUnavailable
from airbyte_cdk.sources.streams.concurrent.exceptions import ExceptionWithDisplayMessage


@pytest.mark.parametrize(
    "stream_availability, expected_available, expected_message",
    [
        pytest.param(StreamAvailable(), True, None, id="test_stream_is_available"),
        pytest.param(STREAM_AVAILABLE, True, None, id="test_stream_is_available_using_singleton"),
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


@pytest.mark.parametrize(
    "exception, expected_display_message",
    [
        pytest.param(Exception("message"), None, id="test_no_display_message"),
        pytest.param(ExceptionWithDisplayMessage("message"), "message", id="test_no_display_message"),
    ],
)
def test_get_error_display_message(exception, expected_display_message):
    stream = Mock()
    facade = StreamFacade(stream)

    display_message = facade.get_error_display_message(exception)

    assert display_message == expected_display_message
