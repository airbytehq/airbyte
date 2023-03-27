#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module groups steps made to run tests for a specific Python connector given a test context."""

from abc import ABC
from typing import List, Tuple

import asyncer
from ci_connector_ops.pipelines.actions import environments, secrets
from ci_connector_ops.pipelines.bases import Step, StepResult, StepStatus
from ci_connector_ops.pipelines.contexts import ConnectorTestContext
from ci_connector_ops.pipelines.tests.common import AcceptanceTests
from ci_connector_ops.pipelines.utils import check_path_in_workdir
from dagger import Container


class CodeFormatChecks(Step):
    title = "Code format checks"

    RUN_BLACK_CMD = ["python", "-m", "black", f"--config=/{environments.PYPROJECT_TOML_FILE_PATH}", "--check", "."]
    RUN_ISORT_CMD = ["python", "-m", "isort", f"--settings-file=/{environments.PYPROJECT_TOML_FILE_PATH}", "--check-only", "--diff", "."]
    RUN_FLAKE_CMD = ["python", "-m", "pflake8", f"--config=/{environments.PYPROJECT_TOML_FILE_PATH}", "."]

    async def run(self) -> List[StepResult]:
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

    async def run(self) -> Tuple[StepResult, Container]:
        """Install the connector under test package in a Python container.

        Returns:
            Tuple[StepResult, Container]: Failure or success of the package installation and the connector under test container (with the connector package installed).
        """
        connector_under_test = await environments.with_installed_airbyte_connector(self.context)
        return await self.get_step_result(connector_under_test), connector_under_test


class PythonTests(Step, ABC):
    async def _run_tests_in_directory(self, connector_under_test: Container, test_directory: str) -> StepResult:
        """Runs the pytest tests in the test_directory that was passed.
        A StepStatus.SKIPPED is returned if no tests were discovered.
        Args:
            connector_under_test (Container): The connector under test container.
            test_directory (str): The directory in which the python test modules are declared

        Returns:
            Tuple[StepStatus, Optional[str], Optional[str]]: Tuple of StepStatus, stderr and stdout.
        """
        test_config = (
            "pytest.ini" if await check_path_in_workdir(connector_under_test, "pytest.ini") else "/" + environments.PYPROJECT_TOML_FILE_PATH
        )
        if await check_path_in_workdir(connector_under_test, test_directory):
            tester = connector_under_test.with_exec(
                [
                    "python",
                    "-m",
                    "pytest",
                    "--suppress-tests-failed-exit-code",
                    "--suppress-no-test-exit-code",
                    "-s",
                    test_directory,
                    "-c",
                    test_config,
                ]
            )
            return self.pytest_logs_to_step_result(await tester.stdout())

        else:
            return StepResult(self, StepStatus.SKIPPED)


class UnitTests(PythonTests):
    title = "Unit tests"

    async def run(self, connector_under_test: Container) -> StepResult:
        """Run all pytest tests declared in the unit_tests directory of the connector code.

        Args:
            connector_under_test (Container): The connector under test container.

        Returns:
            StepResult: Failure or success of the unit tests with stdout and stdout.
        """
        connector_under_test = self.get_dagger_pipeline(connector_under_test)
        return await self._run_tests_in_directory(connector_under_test, "unit_tests")


class IntegrationTests(PythonTests):
    title = "Integration tests"

    async def run(self, connector_under_test: Container) -> StepResult:
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


async def run_all_tests(context: ConnectorTestContext) -> List[StepResult]:
    package_install_results, connector_under_test = await ConnectorInstallTest(context).run()
    unit_tests_results = await UnitTests(context).run(connector_under_test)
    results = [
        package_install_results,
        unit_tests_results,
    ]

    if unit_tests_results.status is StepStatus.FAILURE:
        return results + [IntegrationTests(context).skip(), AcceptanceTests(context).skip()]

    context.secrets_dir = await secrets.get_connector_secret_dir(context)
    async with asyncer.create_task_group() as task_group:
        tasks = [
            task_group.soonify(IntegrationTests(context).run)(connector_under_test),
            task_group.soonify(AcceptanceTests(context).run)(),
        ]

    return results + [task.value for task in tasks]


async def run_code_format_checks(context: ConnectorTestContext) -> List[StepResult]:
    return await CodeFormatChecks(context).run()
