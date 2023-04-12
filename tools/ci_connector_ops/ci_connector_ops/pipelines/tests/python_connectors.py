#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module groups steps made to run tests for a specific Python connector given a test context."""

from typing import List, Tuple

import asyncer
from ci_connector_ops.pipelines.actions import environments, secrets
from ci_connector_ops.pipelines.bases import Step, StepResult, StepStatus
from ci_connector_ops.pipelines.contexts import ConnectorTestContext
from ci_connector_ops.pipelines.tests.common import AcceptanceTests, PytestStep
from dagger import Container, File


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
            context (ConnectorTestContext): The current test context, providing a connector object, a dagger client and a repository directory.
            step (Step): The step in which the code format checks are run. Defaults to Step.CODE_FORMAT_CHECKS
        Returns:
            StepResult: Failure or success of the code format checks with stdout and stderr.
        """
        connector_under_test = environments.with_airbyte_connector(self.context)
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

    async def _run(self) -> Tuple[StepResult, Container]:
        """Install the connector under test package in a Python container.

        Returns:
            Tuple[StepResult, Container]: Failure or success of the package installation and the connector under test container (with the connector package installed).
        """
        connector_under_test = await environments.with_installed_airbyte_connector(self.context)
        return await self.get_step_result(connector_under_test), connector_under_test


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
        return await self._run_tests_in_directory(connector_under_test, "unit_tests")


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
        connector_under_test_with_secrets = connector_under_test.with_directory(
            f"{self.context.connector.code_directory}/secrets", self.context.secrets_dir
        )

        return await self._run_tests_in_directory(connector_under_test_with_secrets, "integration_tests")


class BuildConnectorImage(Step):
    """
    A step to build a Python connector image using its Dockerfile.

    Export the image as a tar archive on the host /tmp folder.
    """

    title = "Build connector image"

    async def _run(self) -> Tuple[StepResult, File]:
        connector_dir = self.context.get_connector_dir()
        connector_local_tar_name = f"{self.context.connector.technical_name}.tar"
        export_success = await connector_dir.docker_build().export(f"/tmp/{connector_local_tar_name}")
        if export_success:
            connector_image_tar_path = (
                self.context.dagger_client.host().directory("/tmp", include=[connector_local_tar_name]).file(connector_local_tar_name)
            )
            return StepResult(self, StepStatus.SUCCESS), connector_image_tar_path
        else:
            return StepResult(self, StepStatus.FAILURE, stderr="The connector image could not be exported."), None


async def run_all_tests(context: ConnectorTestContext) -> List[StepResult]:
    """Run all tests for a Python connnector.

    Args:
        context (ConnectorTestContext): The current connector test context.

    Returns:
        List[StepResult]: _description_
    """
    connector_package_install_step = ConnectorPackageInstall(context)
    unit_tests_step = UnitTests(context)
    build_connector_image_step = BuildConnectorImage(context)
    integration_tests_step = IntegrationTests(context)
    acceptance_test_step = AcceptanceTests(context)

    context.logger.info("Run the connector package install step.")
    package_install_results, connector_under_test = await connector_package_install_step.run()
    context.logger.info("Successfully ran the connector package install step.")

    context.logger.info("Run the unit tests step.")
    unit_tests_results = await unit_tests_step.run(connector_under_test)

    results = [
        package_install_results,
        unit_tests_results,
    ]

    if unit_tests_results.status is StepStatus.FAILURE:
        return results + [build_connector_image_step.skip(), integration_tests_step.skip(), acceptance_test_step.skip()]
    context.logger.info("Successfully ran the unit tests step.")

    if not context.connector.acceptance_test_config["connector_image"].endswith(":dev"):
        context.logger.info("Not building the connector image as CAT is run with a non dev version of the connector.")
        connector_image_tar_file = None
    else:
        context.logger.info("Run the build connector image step.")
        build_connector_image_results, connector_image_tar_file = await build_connector_image_step.run()
        results.append(build_connector_image_results)
        if build_connector_image_results.status is StepStatus.FAILURE:
            return results + [integration_tests_step.skip(), acceptance_test_step.skip()]
        context.logger.info("Successfully ran the build connector image step.")

    context.logger.info("Retrieve the connector secrets.")
    context.secrets_dir = await secrets.get_connector_secret_dir(context)
    context.logger.info("Run integration tests and acceptance tests in parallel.")
    async with asyncer.create_task_group() as task_group:
        tasks = [
            task_group.soonify(IntegrationTests(context).run)(connector_under_test),
            task_group.soonify(AcceptanceTests(context).run)(connector_image_tar_file),
        ]

    return results + [task.value for task in tasks]


async def run_code_format_checks(context: ConnectorTestContext) -> List[StepResult]:
    """Run the code format check steps for Python connectors.

    Args:
        context (ConnectorTestContext): The current connector test context.

    Returns:
        List[StepResult]: Results of the code format checks.
    """
    return [await CodeFormatChecks(context).run()]
