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
    title = "Code format checks"

    RUN_BLACK_CMD = ["python", "-m", "black", f"--config=/{environments.PYPROJECT_TOML_FILE_PATH}", "--check", "."]
    RUN_ISORT_CMD = ["python", "-m", "isort", f"--settings-file=/{environments.PYPROJECT_TOML_FILE_PATH}", "--check-only", "--diff", "."]
    RUN_FLAKE_CMD = ["python", "-m", "pflake8", f"--config=/{environments.PYPROJECT_TOML_FILE_PATH}", "."]

    async def _run(self) -> List[StepResult]:
        """Run a code format check on the container source code.
        We call black, isort and flake commands:
        - Black formats the code: fails if the code is not formatted.
        - Isort checks the import orders: fails if the import are not properly ordered.
        - Flake enforces style-guides: fails if the style-guide is not followed.
        Args:
            context (ConnectorTestContext): The current test context, providing a connector object, a dagger client and a repository directory.
            step (Step): The step in which the code format checks are run. Defaults to Step.CODE_FORMAT_CHECKS
        Returns:
            List[StepResult]: Failure or success of the code format checks with stdout and stdout in a list.
        """

        connector_under_test = environments.with_airbyte_connector(self.context)
        connector_under_test = self.get_dagger_pipeline(connector_under_test)
        formatter = (
            connector_under_test.with_exec(["echo", "Running black"])
            .with_exec(self.RUN_BLACK_CMD)
            .with_exec(["echo", "Running Isort"])
            .with_exec(self.RUN_ISORT_CMD)
            .with_exec(["echo", "Running Flake"])
            .with_exec(self.RUN_FLAKE_CMD)
        )
        return [await self.get_step_result(formatter)]


class ConnectorInstallTest(Step):
    title = "Connector package install"

    async def _run(self) -> Tuple[StepResult, Container]:
        """Install the connector under test package in a Python container.

        Returns:
            Tuple[StepResult, Container]: Failure or success of the package installation and the connector under test container (with the connector package installed).
        """
        connector_under_test = await environments.with_installed_airbyte_connector(self.context)
        return await self.get_step_result(connector_under_test), connector_under_test


class UnitTests(PytestStep):
    title = "Unit tests"

    async def _run(self, connector_under_test: Container) -> StepResult:
        """Run all pytest tests declared in the unit_tests directory of the connector code.

        Args:
            connector_under_test (Container): The connector under test container.

        Returns:
            StepResult: Failure or success of the unit tests with stdout and stdout.
        """
        connector_under_test = self.get_dagger_pipeline(connector_under_test)
        return await self._run_tests_in_directory(connector_under_test, "unit_tests")


class IntegrationTests(PytestStep):
    title = "Integration tests"

    async def _run(self, connector_under_test: Container) -> StepResult:
        """Run all pytest tests declared in the integration_tests directory of the connector code.

        Args:
            connector_under_test (Container): The connector under test container.

        Returns:
            StepResult: Failure or success of the integration tests with stdout and stdout.
        """
        connector_under_test = self.get_dagger_pipeline(connector_under_test)
        connector_under_test_with_secrets = connector_under_test.with_directory(
            f"{self.context.connector.code_directory}/secrets", self.context.secrets_dir
        )

        return await self._run_tests_in_directory(connector_under_test_with_secrets, "integration_tests")


class BuildConnectorImage(Step):
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
    connector_install_step = ConnectorInstallTest(context)
    unit_tests_step = UnitTests(context)
    build_connector_image_step = BuildConnectorImage(context)
    integration_tests_step = IntegrationTests(context)
    acceptance_test_step = AcceptanceTests(context)

    package_install_results, connector_under_test = await connector_install_step.run()
    unit_tests_results = await unit_tests_step.run(connector_under_test)

    results = [
        package_install_results,
        unit_tests_results,
    ]

    if unit_tests_results.status is StepStatus.FAILURE:
        return results + [build_connector_image_step.skip(), integration_tests_step.skip(), acceptance_test_step.skip()]

    if context.connector.acceptance_test_config["connector_image"].endswith(":dev"):
        build_connector_image_results, connector_image_tar_file = await build_connector_image_step.run()
        results.append(build_connector_image_results)
        if build_connector_image_results.status is StepStatus.FAILURE:
            return results + [integration_tests_step.skip(), acceptance_test_step.skip()]
    else:
        context.logger.info("Not building the connector image as CAT is run with a non dev version")
        connector_image_tar_file = None

    context.secrets_dir = await secrets.get_connector_secret_dir(context)
    async with asyncer.create_task_group() as task_group:
        tasks = [
            task_group.soonify(IntegrationTests(context).run)(connector_under_test),
            task_group.soonify(AcceptanceTests(context).run)(connector_image_tar_file),
        ]

    return results + [task.value for task in tasks]


async def run_code_format_checks(context: ConnectorTestContext) -> List[StepResult]:
    return await CodeFormatChecks(context).run()
