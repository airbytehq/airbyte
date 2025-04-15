# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

"""Airbyte standard connector tests.

The FAST Airbyte Standard Tests suite is designed to ensure that connectors meet Airbyte
protocol standards.
"""

import pytest
from source_hubspot import SourceHubspot

from airbyte_cdk.test.declarative.test_suites import (
    SourceTestSuiteBase,
    generate_tests,
)


def pytest_generate_tests(metafunc) -> None:
    generate_tests(metafunc)


@pytest.mark.slow
@pytest.mark.requires_creds
class TestAirbyteStandardTests(SourceTestSuiteBase):
    """Test suite for the Airbyte standard tests.

    This class inherits from SourceTestSuiteBase and implements all of the tests in the suite.

    As long as the class name starts with "Test", pytest will automatically discover and run the
    tests in this class.
    """

    connector = SourceHubspot
