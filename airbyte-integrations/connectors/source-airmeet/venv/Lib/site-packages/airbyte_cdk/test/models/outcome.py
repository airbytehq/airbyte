# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
"""Run acceptance tests in PyTest.

These tests leverage the same `acceptance-test-config.yml` configuration files as the
acceptance tests in CAT, but they run in PyTest instead of CAT. This allows us to run
the acceptance tests in the same local environment as we are developing in, speeding
up iteration cycles.
"""

from __future__ import annotations

from enum import Enum, auto


class ExpectedOutcome(Enum):
    """Enum to represent the expected outcome of a test scenario.

    Class supports comparisons to a boolean or None.
    """

    EXPECT_EXCEPTION = auto()
    EXPECT_SUCCESS = auto()
    ALLOW_ANY = auto()

    @classmethod
    def from_status_str(cls, status: str | None) -> ExpectedOutcome:
        """Convert a status string to an ExpectedOutcome."""
        if status is None:
            return ExpectedOutcome.ALLOW_ANY

        try:
            return {
                "succeed": ExpectedOutcome.EXPECT_SUCCESS,
                "failed": ExpectedOutcome.EXPECT_EXCEPTION,
                "exception": ExpectedOutcome.EXPECT_EXCEPTION,  # same as 'failed'
            }[status]
        except KeyError as ex:
            raise ValueError(
                f"Invalid status '{status}'. Expected 'succeed', 'failed', or 'exception'.",
            ) from ex

    @classmethod
    def from_expecting_exception_bool(cls, expecting_exception: bool | None) -> ExpectedOutcome:
        """Convert a boolean indicating whether an exception is expected to an ExpectedOutcome."""
        if expecting_exception is None:
            # Align with legacy behavior where default would be 'False' (no exception expected)
            return ExpectedOutcome.EXPECT_SUCCESS

        return (
            ExpectedOutcome.EXPECT_EXCEPTION
            if expecting_exception
            else ExpectedOutcome.EXPECT_SUCCESS
        )

    def expect_exception(self) -> bool:
        """Return whether the expectation is that an exception should be raised."""
        return self == ExpectedOutcome.EXPECT_EXCEPTION

    def expect_success(self) -> bool:
        """Return whether the expectation is that the test should succeed without exceptions."""
        return self == ExpectedOutcome.EXPECT_SUCCESS
