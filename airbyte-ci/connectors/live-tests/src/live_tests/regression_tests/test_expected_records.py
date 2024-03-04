import pytest

pytestmark = [
    pytest.mark.anyio,
]

async def test_all_records_are_produced_in_target_version(read_control_execution_result, read_target_execution_result):
    assert read_control_execution_result == read_target_execution_result