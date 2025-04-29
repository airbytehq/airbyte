
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""FAST Airbyte Standard Tests for the source_pokeapi_w_components source."""

#from airbyte_cdk.test.standard_tests import SourceTestSuiteBase
from pathlib import Path

from airbyte_cdk.test.standard_tests import SourceTestSuiteBase
from airbyte_cdk.test.standard_tests.util import create_connector_test_suite


pytest_plugins = [
    "airbyte_cdk.test.standard_tests.pytest_hooks",
]

class TestSuite(SourceTestSuiteBase):
    """Test suite for Python sources.

    This class inherits from SourceTestSuiteBase and implements all of the tests in the suite.

    As long as the class name starts with "Test", pytest will automatically discover and run the
    tests in this class.
    """
