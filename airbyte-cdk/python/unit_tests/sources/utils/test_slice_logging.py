#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging

import pytest
from airbyte_cdk.models import AirbyteLogMessage, AirbyteMessage, Level
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.sources.utils.slice_logging import DebugSliceLogger


@pytest.mark.parametrize(
    "level, should_log",
    [
        pytest.param(logging.DEBUG, True, id="should_log_if_level_is_debug"),
        pytest.param(logging.INFO, False, id="should_log_if_level_is_debug"),
        pytest.param(logging.WARN, False, id="should_log_if_level_is_debug"),
        pytest.param(logging.WARNING, False, id="should_log_if_level_is_debug"),
        pytest.param(logging.ERROR, False, id="should_log_if_level_is_debug"),
        pytest.param(logging.CRITICAL, False, id="should_log_if_level_is_debug"),
    ],
)
def test_should_log_slice_message(level, should_log):
    logger = logging.Logger(name="name", level=level)
    assert DebugSliceLogger().should_log_slice_message(logger) == should_log


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
