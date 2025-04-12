# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""Airbyte Standard Tests

We import Standard Test class from the CDK. This gives us the ability to step-debug tests and
iterate locally and quickly.
"""

from source_hardcoded_records import SourceHardcodedRecords

from airbyte_cdk.test.declarative.test_suites import (
    ConnectorTestScenario,
    SourceTestSuiteBase,
    generate_tests,
)


def pytest_generate_tests(metafunc) -> None:
    generate_tests(metafunc)


class TestHardcodedRecords(SourceTestSuiteBase):
    """Connector standard test suite class.

    This class inherits from SourceTestSuiteBase and implements all of the tests in the suite.

    As long as the class name starts with "Test", pytest will automatically discover and run the
    tests in this class and in its base classes.
    """

    connector = SourceHardcodedRecords

    @classmethod
    def create_connector(cls, scenario: ConnectorTestScenario) -> "IConnector":
        """Create a new instance of the connector."""

        return SourceHardcodedRecords()
