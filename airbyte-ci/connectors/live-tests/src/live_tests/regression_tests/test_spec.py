# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
from __future__ import annotations

from collections.abc import Callable

import pytest
from airbyte_protocol.models import Type  # type: ignore
from live_tests.commons.models import ExecutionResult
from live_tests.utils import fail_test_on_failing_execution_results

pytestmark = [
    pytest.mark.anyio,
]


async def test_spec_passes_on_both_versions(
    record_property: Callable,
    spec_control_execution_result: ExecutionResult,
    spec_target_execution_result: ExecutionResult,
) -> None:
    """This test runs the spec command on both the control and target connectors.
    It makes sure that the spec command succeeds on both connectors by checking the presence of a SPEC message.
    """
    fail_test_on_failing_execution_results(
        record_property,
        [
            spec_control_execution_result,
            spec_target_execution_result,
        ],
    )

    def has_spec(execution_result: ExecutionResult) -> bool:
        for message in execution_result.airbyte_messages:
            if message.type is Type.SPEC and message.spec:
                return True
        return False

    if not has_spec(spec_control_execution_result):
        pytest.skip("The control spec did not succeed, we cannot compare the results.")
    if not has_spec(spec_target_execution_result):
        pytest.fail("The target spec did not succeed. Check the test artifacts for more information.")
