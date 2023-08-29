#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging

import pytest
from airbyte_cdk.models import AirbyteLogMessage, AirbyteMessage, Level
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.sources.utils.slice_logger import AlwaysLogSliceLogger, DebugSliceLogger


@pytest.mark.parametrize(
    "slice_logger, level, should_log",
    [
        pytest.param(DebugSliceLogger(), logging.DEBUG, True, id="debug_logger_should_log_if_level_is_debug"),
        pytest.param(DebugSliceLogger(), logging.INFO, False, id="debug_logger_should_not_log_if_level_is_info"),
        pytest.param(DebugSliceLogger(), logging.WARN, False, id="debug_logger_should_not_log_if_level_is_warn"),
        pytest.param(DebugSliceLogger(), logging.WARNING, False, id="debug_logger_should_not_log_if_level_is_warning"),
        pytest.param(DebugSliceLogger(), logging.ERROR, False, id="debug_logger_should_not_log_if_level_is_error"),
        pytest.param(DebugSliceLogger(), logging.CRITICAL, False, id="always_log_logger_should_not_log_if_level_is_critical"),
        pytest.param(AlwaysLogSliceLogger(), logging.DEBUG, True, id="always_log_logger_should_log_if_level_is_debug"),
        pytest.param(AlwaysLogSliceLogger(), logging.INFO, True, id="always_log_logger_should_log_if_level_is_info"),
        pytest.param(AlwaysLogSliceLogger(), logging.WARN, True, id="always_log_logger_should_log_if_level_is_warn"),
        pytest.param(AlwaysLogSliceLogger(), logging.WARNING, True, id="always_log_logger_should_log_if_level_is_warning"),
        pytest.param(AlwaysLogSliceLogger(), logging.ERROR, True, id="always_log_logger_should_log_if_level_is_error"),
        pytest.param(AlwaysLogSliceLogger(), logging.CRITICAL, True, id="always_log_logger_should_log_if_level_is_critical"),
    ],
)
def test_should_log_slice_message(slice_logger, level, should_log):
    logger = logging.Logger(name="name", level=level)
    assert slice_logger.should_log_slice_message(logger) == should_log


@pytest.mark.parametrize(
    "_slice, expected_message",
    [
        pytest.param(None, "slice:null", id="test_none_slice"),
        pytest.param({}, "slice:{}", id="test_empty_slice"),
        pytest.param({"key": "value"}, 'slice:{"key": "value"}', id="test_dict"),
    ],
)
def test_create_slice_log_message(_slice, expected_message):
    expected_log_message = AirbyteMessage(type=MessageType.LOG, log=AirbyteLogMessage(level=Level.INFO, message=expected_message))
    log_message = DebugSliceLogger().create_slice_log_message(_slice)
    assert log_message == expected_log_message
