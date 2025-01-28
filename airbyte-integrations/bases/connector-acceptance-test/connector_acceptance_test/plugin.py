#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from enum import Enum
from pathlib import Path
from typing import Callable, List, Tuple, Type

import pytest
from _pytest.config import Config
from _pytest.config.argparsing import Parser

from connector_acceptance_test.base import BaseTest
from connector_acceptance_test.config import Config as AcceptanceTestConfig
from connector_acceptance_test.config import GenericTestConfig
from connector_acceptance_test.utils import diff_dicts, load_config


HERE = Path(__file__).parent.absolute()


def pytest_configure(config):
    config.addinivalue_line("markers", "default_timeout: mark test to be wrapped by `timeout` decorator with default value")
    config.addinivalue_line(
        "markers",
        "backward_compatibility: mark test to be part of the backward compatibility tests suite (deselect with '-m \"not backward_compatibility\"')",
    )


def pytest_load_initial_conftests(early_config: Config, parser: Parser, args: List[str]):
    """Hook function to add acceptance tests to args"""
    args.append(str(HERE / "tests"))


def pytest_addoption(parser):
    """Hook function to add CLI option `acceptance-test-config`"""
    parser.addoption(
        "--acceptance-test-config", action="store", default=".", help="Folder with standard test config - acceptance_test_config.yml"
    )


class TestAction(Enum):
    PARAMETRIZE = 1
    SKIP = 2
    FAIL = 3


def pytest_generate_tests(metafunc):
    """Hook function to customize test discovery and parametrization.
    It parametrizes, skips or fails a discovered test according the test configuration.
    """

    if "inputs" in metafunc.fixturenames:
        test_config_key = metafunc.cls.config_key()
        global_config = load_config(metafunc.config.getoption("--acceptance-test-config"))
        test_configuration: GenericTestConfig = getattr(global_config.acceptance_tests, test_config_key, None)
        test_action, reason = parametrize_skip_or_fail(
            metafunc.cls, metafunc.function, global_config.test_strictness_level, test_configuration
        )

        if test_action == TestAction.PARAMETRIZE:
            metafunc.parametrize("inputs", test_configuration.tests)
        if test_action == TestAction.SKIP:
            pytest.skip(reason)
        if test_action == TestAction.FAIL:
            pytest.fail(reason)


def parametrize_skip_or_fail(
    TestClass: Type[BaseTest],
    test_function: Callable,
    global_test_mode: AcceptanceTestConfig.TestStrictnessLevel,
    test_configuration: GenericTestConfig,
) -> Tuple[TestAction, str]:
    """Use the current test strictness level and test configuration to determine if the discovered test should be parametrized, skipped or failed.
    We parametrize a test if:
      - the configuration declares tests.
    We skip a test if:
      - the configuration does not declare tests and:
        - the current test mode allows this test to be skipped.
        - Or a bypass_reason is declared in the test configuration.
    We fail a test if:
        - the configuration does not declare the test but the discovered test is declared as mandatory for the current test strictness level.
    Args:
        TestClass (Type[BaseTest]): The discovered test class
        test_function (Callable): The discovered test function
        global_test_mode (AcceptanceTestConfig.TestStrictnessLevel): The global test strictness level (from the global configuration object)
        test_configuration (GenericTestConfig): The current test configuration.

    Returns:
        Tuple[TestAction, str]: The test action the execution should take and the reason why.
    """
    test_name = f"{TestClass.__name__}.{test_function.__name__}"
    test_mode_can_skip_this_test = global_test_mode not in TestClass.MANDATORY_FOR_TEST_STRICTNESS_LEVELS
    skipping_reason_prefix = f"Skipping {test_name}: "
    default_skipping_reason = skipping_reason_prefix + "not found in the config."

    if test_configuration is None:
        if test_mode_can_skip_this_test:
            return TestAction.SKIP, default_skipping_reason
        else:
            return (
                TestAction.FAIL,
                f"{test_name} failed: it was not configured but must be according to the current {global_test_mode} test strictness level.",
            )
    else:
        if test_configuration.tests is not None:
            return TestAction.PARAMETRIZE, f"Parametrize {test_name}: tests are configured."
        else:
            return TestAction.SKIP, skipping_reason_prefix + test_configuration.bypass_reason


def pytest_collection_modifyitems(config, items):
    """
    Get prepared test items and wrap them with `pytest.mark.timeout(timeout_seconds)` decorator.

    `timeout_seconds` may be received either from acceptance test config or `pytest.mark.default_timeout(timeout_seconds)`,
    if `timeout_seconds` is not specified in the acceptance test config.
    """

    config = load_config(config.getoption("--acceptance-test-config"))

    i = 0
    packed_items = []
    while i < len(items):
        inner_items = [item for item in items if item.originalname == items[i].originalname]
        packed_items.append(inner_items)
        i += len(inner_items)

    for items in packed_items:
        if not hasattr(items[0].cls, "config_key"):
            # Skip user defined test classes from integration_tests/ directory.
            continue
        test_configs = getattr(config.acceptance_tests, items[0].cls.config_key())

        for test_config, item in zip(test_configs.tests, items):
            default_timeout = item.get_closest_marker("default_timeout")
            if test_config.timeout_seconds:
                item.add_marker(pytest.mark.timeout(test_config.timeout_seconds))
            elif default_timeout:
                item.add_marker(pytest.mark.timeout(*default_timeout.args))


def pytest_assertrepr_compare(config, op, left, right):
    if op != "==":
        return

    use_markup = config.get_terminal_writer().hasmarkup
    return diff_dicts(left, right, use_markup=use_markup)
