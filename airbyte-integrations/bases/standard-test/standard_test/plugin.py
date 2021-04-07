import pytest

from .utils import load_config


def pytest_addoption(parser):
    """Hook function to add CLI option `standard_test_config`"""
    parser.addoption(
        "--standard_test_config", action="store", default=".", help="Folder with standard test config - standard_test_config.yml"
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
        config = load_config(metafunc.config.getoption("--standard_test_config"))
        # print(config.dict())
        if not hasattr(config.tests, config_key) or not getattr(config.tests, config_key):
            pytest.skip(f"Skipping {test_name} because not found in the config")
        else:
            test_inputs = getattr(config.tests, config_key)
            if not test_inputs:
                pytest.skip(f"Skipping {test_name} because no inputs provided")

            metafunc.parametrize("inputs", test_inputs)
