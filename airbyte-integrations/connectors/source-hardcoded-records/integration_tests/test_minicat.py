# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""Mini-CAT test for Hardcoded Records Source.

We import the `MiniCAT` class from the CDK. This gives us the ability to step-debug tests and
iterate locally and quickly.
"""

from pathlib import Path

from source_hardcoded_records import SourceHardcodedRecords

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


class TestHardcodedRecords(SourceTestSuiteBase):
    # """Test suite for the source_pokeapi_w_components source.

    # This class inherits from SourceTestSuiteBase and implements all of the tests in the suite.

    # As long as the class name starts with "Test", pytest will automatically discover and run the
    # tests in this class.
    # """

    connector = SourceHardcodedRecords
    working_dir = CONNECTOR_ROOT
    acceptance_test_config_path = get_file_path("acceptance-test-config.yml")

    @classmethod
    def create_connector(cls, scenario: ConnectorTestScenario) -> SourceHardcodedRecords:
        """Create a new instance of the connector."""

        return SourceHardcodedRecords()
