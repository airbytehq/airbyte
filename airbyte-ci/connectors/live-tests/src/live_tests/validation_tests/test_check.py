#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

from typing import Callable

import pytest
from airbyte_protocol.models import Type
from live_tests.commons.models import ExecutionResult
from live_tests.consts import MAX_LINES_IN_REPORT
from live_tests.utils import fail_test_on_failing_execution_results, is_successful_check, tail_file

pytestmark = [
    pytest.mark.anyio,
]


@pytest.mark.allow_diagnostic_mode
async def test_check_succeeds(
    record_property: Callable,
    check_target_execution_result: ExecutionResult,
) -> None:
    """
    Verify that the check command succeeds on the target connection.

    Success is determined by the presence of a connection status message with a status of SUCCEEDED.
    """
    fail_test_on_failing_execution_results(
        record_property,
        [check_target_execution_result],
    )
    assert len([msg for msg in check_target_execution_result.airbyte_messages if msg.type == Type.CONNECTION_STATUS]) == 1

    successful_target_check: bool = is_successful_check(check_target_execution_result)
    error_messages = []
    if not successful_target_check:
        record_property(
            f"Target CHECK standard output  [Last {MAX_LINES_IN_REPORT} lines]",
            tail_file(check_target_execution_result.stdout_file_path, n=MAX_LINES_IN_REPORT),
        )
        error_messages.append("The target check did not succeed. Check the test artifacts for more information.")
    if error_messages:
        pytest.fail("\n".join(error_messages))
