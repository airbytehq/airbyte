# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
from __future__ import annotations

import functools
import logging
import traceback
from collections.abc import Callable
from enum import Enum
from typing import Any

import decorator
from _pytest.config import Config
from live_tests import stash_keys


class TestEvaluationMode(Enum):
    """
    Tests may be run in "diagnostic" mode or "strict" mode.

    When run in "diagnostic" mode, `AssertionError`s won't fail the test, but we will continue to surface
    any errors to the test report.

    In "strict" mode, tests pass/fail as usual.

    In live tests, diagnostic mode is used for tests that don't affect the overall functionality of the
    connector but that test an ideal state of the connector. Currently this is applicable to validation
    tests only.
    """

    DIAGNOSTIC = "diagnostic"
    STRICT = "strict"


def _extract_test_mode_config_from_args(func: Callable, *args: Any, **kwargs: Any) -> Config:
    """
    Get the pytest config from the arguments passed to the test.

    This will allow us to determine the test mode.

    To use the `allow_diagnostic_mode` decorator, the dev is required to pass the `pytestconfig` fixture into the test
    function. We raise a ValueError if the config isn't present to avoid accidental omissions of `pytestconfig`.
    """
    try:
        [config] = [a for a in list(args) + list(kwargs.values()) if isinstance(a, Config)]
    except ValueError:
        raise ValueError(
            f"A config argument is required but was not found for {func.__module__ if hasattr(func, '__module__') else ''}: {func.__name__}"
        )
    return config


def allow_diagnostic_mode(func: Callable) -> Any:
    """
    Decorator for wrapping tests that we want to always pass.

    To use this decorator, the dev is required to pass the `pytestconfig` fixture into the test function.
    """

    @functools.wraps(func)
    async def wrapper(f, *args: Any, **kwargs: Any) -> Any:
        config = _extract_test_mode_config_from_args(func, *args, **kwargs)

        # If tests are running in "diagnostic" mode, log the AssertionErrors but allow the test to pass
        # Otherwise run the test as usual
        if config.stash[stash_keys.VALIDATION_TEST_MODE] == TestEvaluationMode.DIAGNOSTIC:
            try:
                return await func(*args, **kwargs)
            except AssertionError:
                logging.warning(traceback.format_exc())
        else:
            return await func(*args, **kwargs)

    return decorator.decorator(wrapper, func)
