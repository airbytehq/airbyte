"""This module contains the TestStandardTestSuite class.

This is used to run the standard test suite for the destination connector.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from airbyte_connector_tester import DestinationTestSuiteBase
from destination_motherduck.destination import DestinationMotherDuck
from typing_extensions import override


class TestStandardTestSuite(DestinationTestSuiteBase):
    """This class is used to run the standard test suite for the destination connector.

    Test definitions are defined in the base class DestinationTestSuiteBase, which lives
    in the airbyte-connector-tester package.
    """

    acceptance_test_file_path = Path("./acceptance-test-config.json")

    @override
    def new_connector(self, **kwargs: dict[str, Any]) -> DestinationMotherDuck:
        return DestinationMotherDuck()
