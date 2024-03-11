# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import pytest
from live_tests.commons.models import ExecutionResult

from .utils import filter_records, make_comparable_records

pytestmark = [
    pytest.mark.anyio,
]


# This test is very basic and just used as a demonstration before porting the "real" expected records tests from VA
async def test_all_records_are_produced_in_target_version(
    read_with_state_control_execution_result: ExecutionResult,
    read_with_state_target_execution_result: ExecutionResult,
) -> None:
    control_records = list(make_comparable_records(filter_records(read_with_state_control_execution_result.airbyte_messages)))
    target_records = list(make_comparable_records(filter_records(read_with_state_target_execution_result.airbyte_messages)))
    assert target_records == control_records
