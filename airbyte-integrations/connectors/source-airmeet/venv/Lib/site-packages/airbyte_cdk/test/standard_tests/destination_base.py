# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
"""Base class for destination test suites."""

from airbyte_cdk.test.standard_tests.connector_base import ConnectorTestSuiteBase


class DestinationTestSuiteBase(ConnectorTestSuiteBase):
    """Base class for destination test suites.

    This class provides a base set of functionality for testing destination connectors, and it
    inherits all generic connector tests from the `ConnectorTestSuiteBase` class.

    TODO: As of now, this class does not add any additional functionality or tests specific to
    destination connectors. However, it serves as a placeholder for future enhancements and
    customizations that may be needed for destination connectors.
    """
