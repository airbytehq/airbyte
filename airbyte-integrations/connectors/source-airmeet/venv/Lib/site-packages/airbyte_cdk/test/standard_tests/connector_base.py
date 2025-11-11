# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
"""Base class for connector test suites."""

from __future__ import annotations

import importlib
import os
from pathlib import Path
from typing import TYPE_CHECKING, cast

from boltons.typeutils import classproperty

from airbyte_cdk.test import entrypoint_wrapper
from airbyte_cdk.test.models import (
    ConnectorTestScenario,
)
from airbyte_cdk.test.standard_tests._job_runner import IConnector, run_test_job
from airbyte_cdk.test.standard_tests.docker_base import DockerConnectorTestSuite

if TYPE_CHECKING:
    from collections.abc import Callable

    from airbyte_cdk.test import entrypoint_wrapper


class ConnectorTestSuiteBase(DockerConnectorTestSuite):
    """Base class for Python connector test suites."""

    connector: type[IConnector] | Callable[[], IConnector] | None  # type: ignore [reportRedeclaration]
    """The connector class or a factory function that returns an scenario of IConnector."""

    @classproperty  # type: ignore [no-redef]
    def connector(cls) -> type[IConnector] | Callable[[], IConnector] | None:
        """Get the connector class for the test suite.

        This assumes a python connector and should be overridden by subclasses to provide the
        specific connector class to be tested.
        """
        connector_root = cls.get_connector_root_dir()
        connector_name = cls.connector_name

        expected_module_name = connector_name.replace("-", "_").lower()
        expected_class_name = connector_name.replace("-", "_").title().replace("_", "")

        # dynamically import and get the connector class: <expected_module_name>.<expected_class_name>

        cwd_snapshot = Path().absolute()
        os.chdir(connector_root)

        # Dynamically import the module
        try:
            module = importlib.import_module(expected_module_name)
        except ModuleNotFoundError as e:
            raise ImportError(
                f"Could not import module '{expected_module_name}'. "
                "Please ensure you are running from within the connector's virtual environment, "
                "for instance by running `poetry run airbyte-cdk connector test` from the "
                "connector directory. If the issue persists, check that the connector "
                f"module matches the expected module name '{expected_module_name}' and that the "
                f"connector class matches the expected class name '{expected_class_name}'. "
                "Alternatively, you can run `airbyte-cdk image test` to run a subset of tests "
                "against the connector's image."
            ) from e
        finally:
            # Change back to the original working directory
            os.chdir(cwd_snapshot)

        # Dynamically get the class from the module
        try:
            return cast(type[IConnector], getattr(module, expected_class_name))
        except AttributeError as e:
            # We did not find it based on our expectations, so let's check if we can find it
            # with a case-insensitive match.
            matching_class_name = next(
                (name for name in dir(module) if name.lower() == expected_class_name.lower()),
                None,
            )
            if not matching_class_name:
                raise ImportError(
                    f"Module '{expected_module_name}' does not have a class named '{expected_class_name}'."
                ) from e
            return cast(type[IConnector], getattr(module, matching_class_name))

    @classmethod
    def create_connector(
        cls,
        scenario: ConnectorTestScenario | None,
    ) -> IConnector:
        """Instantiate the connector class."""
        connector = cls.connector  # type: ignore
        if connector:
            if callable(connector) or isinstance(connector, type):
                # If the connector is a class or factory function, instantiate it:
                return cast(IConnector, connector())  # type: ignore [redundant-cast]

        # Otherwise, we can't instantiate the connector. Fail with a clear error message.
        raise NotImplementedError(
            "No connector class or connector factory function provided. "
            "Please provide a class or factory function in `cls.connector`, or "
            "override `cls.create_connector()` to define a custom initialization process."
        )

    # Test Definitions

    def test_check(
        self,
        scenario: ConnectorTestScenario,
    ) -> None:
        """Run `connection` acceptance tests."""
        result: entrypoint_wrapper.EntrypointOutput = run_test_job(
            self.create_connector(scenario),
            "check",
            test_scenario=scenario,
            connector_root=self.get_connector_root_dir(),
        )
        assert len(result.connection_status_messages) == 1, (
            f"Expected exactly one CONNECTION_STATUS message. "
            "Got: {result.connection_status_messages!s}"
        )
