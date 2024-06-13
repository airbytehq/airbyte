# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
from __future__ import annotations

from enum import Enum


class TestEvaluationMode(Enum):
    """
    Tests may be run in "diagnostic" mode or "strict" mode.

    When run in "diagnostic" mode, `AssertionError`s won't fail the test, but we will continue to surface
    any errors to the test report.

    In "strict" mode, tests pass/fail as usual.

    In live tests, diagnostic mode is used for tests that don't affect the overall functionality of the
    connector but that test an ideal state of the connector. Currently this is applicable to validation
    tests only.

    The diagnostic mode can be made available to a test using the @pytest.mark.allow_diagnostic_mode decorator,
    and passing in the --validation-test-mode=diagnostic flag.
    """

    DIAGNOSTIC = "diagnostic"
    STRICT = "strict"
