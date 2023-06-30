#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module groups steps made to run tests for a specific Python connector given a test context."""

from typing import List

import asyncer
from ci_connector_ops.pipelines.actions import environments, secrets
from ci_connector_ops.pipelines.bases import Step, StepResult, StepStatus
from ci_connector_ops.pipelines.builds import LOCAL_BUILD_PLATFORM
from ci_connector_ops.pipelines.builds.python_connectors import BuildConnectorImage
from ci_connector_ops.pipelines.contexts import ConnectorContext
from ci_connector_ops.pipelines.helpers.steps import run_steps
from ci_connector_ops.pipelines.tests.common import AcceptanceTests, PytestStep
from ci_connector_ops.pipelines.utils import export_container_to_tarball
from dagger import Container


class CodeFormatChecks(Step):
    """A step to run the code format checks on a Python connector using Black, Isort and Flake."""

    title = "Code format checks"

    RUN_BLACK_CMD = ["python", "-m", "black", f"--config=/{environments.PYPROJECT_TOML_FILE_PATH}", "--check", "."]
    RUN_ISORT_CMD = ["python", "-m", "isort", f"--settings-file=/{environments.PYPROJECT_TOML_FILE_PATH}", "--check-only", "--diff", "."]
    RUN_FLAKE_CMD = ["python", "-m", "pflake8", f"--config=/{environments.PYPROJECT_TOML_FILE_PATH}", "."]

    async def _run(self) -> StepResult:
        """Run a code format check on the container source code.

        We call black, isort and flake commands:
        - Black formats the code: fails if the code is not formatted.
        - Isort checks the import orders: fails if the import are not properly ordered.
        - Flake enforces style-guides: fails if the style-guide is not followed.

        Args:
            context (ConnectorContext): The current test context, providing a connector object, a dagger client and a repository directory.
            step (Step): The step in which the code format checks are run. Defaults to Step.CODE_FORMAT_CHECKS
        Returns:
            StepResult: Failure or success of the code format checks with stdout and stderr.
        """
        connector_under_test = environments.with_python_connector_source(self.context)

        formatter = (
            connector_under_test.with_exec(["echo", "Running black"])
            .with_exec(self.RUN_BLACK_CMD)
            .with_exec(["echo", "Running Isort"])
            .with_exec(self.RUN_ISORT_CMD)
            .with_exec(["echo", "Running Flake"])
            .with_exec(self.RUN_FLAKE_CMD)
        )
        return await self.get_step_result(formatter)


class ConnectorPackageInstall(Step):
    """A step to install the Python connector package in a container."""

    title = "Connector package install"
    max_retries = 3

    async def _run(self) -> StepResult:
        """Install the connector under test package in a Python container.

        Returns:
            StepResult: Failure or success of the package installation and the connector under test container (with the connector package installed).
        """
        connector_under_test = await environments.with_python_connector_installed(self.context)
        return await self.get_step_result(connector_under_test)


class UnitTests(PytestStep):
    """A step to run the connector unit tests with Pytest."""

    title = "Unit tests"

    async def _run(self, connector_under_test: Container) -> StepResult:
        """Run all pytest tests declared in the unit_tests directory of the connector code.

        Args:
            connector_under_test (Container): The connector under test container.

        Returns:
            StepResult: Failure or success of the unit tests with stdout and stdout.
        """
        connector_under_test_with_secrets = environments.with_mounted_connector_secrets(self.context, connector_under_test)
        return await self._run_tests_in_directory(connector_under_test_with_secrets, "unit_tests")


class IntegrationTests(PytestStep):
    """A step to run the connector integration tests with Pytest."""

    title = "Integration tests"

    async def _run(self, connector_under_test: Container) -> StepResult:
        """Run all pytest tests declared in the integration_tests directory of the connector code.

        Args:
            connector_under_test (Container): The connector under test container.

        Returns:
            StepResult: Failure or success of the integration tests with stdout and stdout.
        """
        connector_under_test = environments.with_bound_docker_host(self.context, connector_under_test)
        connector_under_test = environments.with_mounted_connector_secrets(self.context, connector_under_test)

        return await self._run_tests_in_directory(connector_under_test, "integration_tests")


async def run_all_tests(context: ConnectorContext) -> List[StepResult]:
    """Run all tests for a Python connector.

    Args:
        context (ConnectorContext): The current connector context.

    Returns:
        List[StepResult]: The results of all the steps that ran or were skipped.
    """

    step_results = await run_steps(
        [
            ConnectorPackageInstall(context),
            BuildConnectorImage(context, LOCAL_BUILD_PLATFORM),
        ]
    )
    if any([step_result.status is StepStatus.FAILURE for step_result in step_results]):
        return step_results
    connector_package_install_results, build_connector_image_results = step_results[0], step_results[1]
    connector_image_tar_file, _ = await export_container_to_tarball(context, build_connector_image_results.output_artifact)
    connector_container = connector_package_install_results.output_artifact

    context.connector_secrets = await secrets.get_connector_secrets(context)

    unit_test_results = await UnitTests(context).run(connector_container)

    if unit_test_results.status is StepStatus.FAILURE:
        return step_results + [unit_test_results]
    step_results.append(unit_test_results)
    async with asyncer.create_task_group() as task_group:
        tasks = [
            task_group.soonify(IntegrationTests(context).run)(connector_container),
            task_group.soonify(AcceptanceTests(context).run)(connector_image_tar_file),
        ]

    return step_results + [task.value for task in tasks]


async def run_code_format_checks(context: ConnectorContext) -> List[StepResult]:
    """Run the code format check steps for Python connectors.

    Args:
        context (ConnectorContext): The current connector context.

    Returns:
        List[StepResult]: Results of the code format checks.
    """
    return [await CodeFormatChecks(context).run()]
