# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""FAST test for Hardcoded Records Source.

We import the FAST class from the CDK. This gives us the ability to step-debug tests and
iterate locally and quickly.
"""

from pathlib import Path

from source_s3.v4 import SourceS3

from airbyte_cdk.test.declarative.test_suites import (
    ConnectorTestScenario,
    SourceTestSuiteBase,
    generate_tests,
)


CONNECTOR_ROOT = Path(__file__).parent.parent


def get_file_path(file_name: str) -> Path:
    """Get the path to a resource file."""
    return CONNECTOR_ROOT / file_name


def pytest_generate_tests(metafunc) -> None:
    generate_tests(metafunc)


class TestSourceS3(SourceTestSuiteBase):
    # """Fast Airbyte Standard Test (FAST) suite for source-s3.

    # This class inherits from SourceTestSuiteBase and implements all of the tests in the suite.

    # As long as the class name starts with "Test", pytest will automatically discover and run the
    # tests in this class.
    # """

    connector = SourceS3
    working_dir = CONNECTOR_ROOT
    acceptance_test_config_path = get_file_path("acceptance-test-config.yml")

    @classmethod
    def create_connector(cls, scenario: ConnectorTestScenario) -> SourceS3:
        """Create a new instance of the connector."""

        return SourceS3()
