# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import re

from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput


def is_in_logs(pattern: str, output: EntrypointOutput) -> bool:
    """Check if any log message case-insensitive matches the pattern."""
    return any(re.search(pattern, entry.log.message, flags=re.IGNORECASE) for entry in output.logs)


def is_not_in_logs(pattern: str, output: EntrypointOutput) -> bool:
    """Check if no log message matches the pattern."""
    return not is_in_logs(pattern, output)


def assert_good_read(output: EntrypointOutput, expected_record_count: int) -> None:
    """Check if the output is successful read with an expected record count and no errors."""
    assert len(output.errors) == 0
    assert len(output.records) == expected_record_count
    assert is_not_in_logs("error|exception", output)


def assert_bad_read(output: EntrypointOutput, expected_record_count: int) -> None:
    """Check if the output is unsuccessful read with an expected record count and errors."""
    assert len(output.records) == expected_record_count
    assert is_in_logs("error|exception", output)
