"""Airbyte standard connector tests.

The AST (Airbyte Standard Tests) suite is designed to ensure that connectors meet Airbyte
protocol standards.
"""

from pathlib import Path

import pytest
from source_hubspot import SourceHubspot

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


@pytest.mark.slow
@pytest.mark.requires_creds
class TestAirbyteStandardTests(SourceTestSuiteBase):
    """Test suite for the Airbyte standard tests.

    This class inherits from SourceTestSuiteBase and implements all of the tests in the suite.

    As long as the class name starts with "Test", pytest will automatically discover and run the
    tests in this class.
    """

    connector = SourceHubspot
    working_dir = CONNECTOR_ROOT
    acceptance_test_config_path = get_file_path("acceptance-test-config.yml")

    @classmethod
    def create_connector(cls, scenario: ConnectorTestScenario) -> SourceHubspot:
        """Create a new instance of the connector."""

        return SourceHubspot()
