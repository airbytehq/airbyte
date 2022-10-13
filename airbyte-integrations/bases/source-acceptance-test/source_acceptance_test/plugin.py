#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from pathlib import Path
from typing import List

import pytest
from _pytest.config import Config
from _pytest.config.argparsing import Parser
from source_acceptance_test.utils import diff_dicts, load_config

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


def pytest_generate_tests(metafunc):
    """Hook function to customize test discovery and parametrization.
    It does two things:
     1. skip test class if its name omitted in the config file (or it has no inputs defined)
     2. parametrize each test with inputs from config file.

    For example config file contains this:
        tests:
          test_suite1:
            - input1: value1
              input2: value2
            - input1: value3
              input2: value4
          test_suite2: []

    Hook function will skip test_suite2 and test_suite3, but parametrize test_suite1 with two sets of inputs.
    """

    if "inputs" in metafunc.fixturenames:
        config_key = metafunc.cls.config_key()
        test_name = f"{metafunc.cls.__name__}.{metafunc.function.__name__}"
        config = load_config(metafunc.config.getoption("--acceptance-test-config"))
        if not hasattr(config.tests, config_key) or not getattr(config.tests, config_key):
            pytest.skip(f"Skipping {test_name} because not found in the config")
        else:
            test_inputs = getattr(config.tests, config_key)
            if not test_inputs:
                pytest.skip(f"Skipping {test_name} because no inputs provided")

            metafunc.parametrize("inputs", test_inputs)


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
        test_configs = getattr(config.tests, items[0].cls.config_key())
        for test_config, item in zip(test_configs, items):
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
