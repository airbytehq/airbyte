"""
MIT License

Copyright (c) 2020 Airbyte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import pytest

from standard_test.utils import load_config


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
        if not hasattr(config.tests, config_key) or not getattr(config.tests, config_key):
            pytest.skip(f"Skipping {test_name} because not found in the config")
        else:
            test_inputs = getattr(config.tests, config_key)
            if not test_inputs:
                pytest.skip(f"Skipping {test_name} because no inputs provided")

            metafunc.parametrize("inputs", test_inputs)
