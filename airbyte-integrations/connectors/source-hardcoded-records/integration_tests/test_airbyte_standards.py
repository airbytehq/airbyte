# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""Airbyte standard connector tests.

The FAST Airbyte Standard Tests suite is designed to ensure that connectors meet Airbyte
protocol standards.
"""

from source_hardcoded_records import SourceHardcodedRecords

from airbyte_cdk.test import standard_tests


pytest_plugins = ["airbyte_cdk.test.standard_tests.pytest_hooks"]


class TestAirbyteStandardTests(standard_tests.SourceTestSuiteBase):
    """Test suite for the Airbyte standard tests.

    This class inherits from SourceTestSuiteBase and implements all of the tests in the suite.

    As long as the class name starts with "Test", pytest will automatically discover and run the
    tests in this class.
    """

    connector = SourceHardcodedRecords
