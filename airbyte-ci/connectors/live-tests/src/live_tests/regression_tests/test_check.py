# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
from __future__ import annotations

from collections.abc import Callable

import pytest
from airbyte_protocol.models import Status, Type  # type: ignore

from live_tests.commons.models import ExecutionResult
from live_tests.consts import MAX_LINES_IN_REPORT
from live_tests.utils import fail_test_on_failing_execution_results, is_successful_check, tail_file

pytestmark = [
    pytest.mark.anyio,
]


async def test_check_passes_on_both_versions(
    record_property: Callable,
    check_control_execution_result: ExecutionResult,
    check_target_execution_result: ExecutionResult,
) -> None:
    """This test runs the check command on both the control and target connectors.
    It makes sure that the check command succeeds on both connectors.
    Success is determined by the presence of a connection status message with a status of SUCCEEDED.
    """
    fail_test_on_failing_execution_results(
        record_property,
        [
            check_control_execution_result,
            check_target_execution_result,
        ],
    )

    successful_control_check: bool = is_successful_check(check_control_execution_result)
    successful_target_check: bool = is_successful_check(check_target_execution_result)
    error_messages = []
    if not successful_control_check:
        record_property(
            f"Control CHECK standard output [Last {MAX_LINES_IN_REPORT} lines]",
            tail_file(check_control_execution_result.stdout_file_path, n=MAX_LINES_IN_REPORT),
        )
        error_messages.append("The control check did not succeed, we cannot compare the results.")
    if not successful_target_check:
        record_property(
            f"Target CHECK standard output  [Last {MAX_LINES_IN_REPORT} lines]",
            tail_file(check_target_execution_result.stdout_file_path, n=MAX_LINES_IN_REPORT),
        )
        error_messages.append("The target check did not succeed. Check the test artifacts for more information.")
    if error_messages:
        pytest.fail("\n".join(error_messages))
