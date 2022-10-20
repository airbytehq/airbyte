#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from pydantic import ValidationError


class StrictModeError(ValidationError):
    pass


def check_all_tests_are_declared(values: dict):
    missing_tests = [test_name for test_name, test_config in values["acceptance_tests"].dict().items() if test_config is None]
    if missing_tests:
        raise ValueError(f"Strict mode is enabled, all tests should be configured. Missing test configurations: {', '.join(missing_tests)}")


VALIDATORS = [check_all_tests_are_declared]
