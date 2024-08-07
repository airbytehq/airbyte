import re

from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput


def is_in_logs(pattern: str, output: EntrypointOutput) -> bool:
    return any(re.search(pattern, entry.log.message, flags=re.IGNORECASE) for entry in output.logs)


def is_not_in_logs(pattern: str, output: EntrypointOutput) -> bool:
    return not is_in_logs(pattern, output)


def assert_good_read(output: EntrypointOutput, expected_record_count: int) -> None:
    # checks there are no errors in output, plus the amount of records is correct.
    assert len(output.errors) == 0
    assert len(output.records) == expected_record_count
    assert is_not_in_logs("error|exception", output)


def assert_bad_read(output: EntrypointOutput, expected_record_count: int) -> None:
    # checks there are errors in output, plus the amount of records expected amount of records.
    assert len(output.records) == expected_record_count
    assert is_in_logs("error|exception", output)
