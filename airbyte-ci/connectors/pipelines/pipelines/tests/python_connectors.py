#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module groups steps made to run tests for a specific Python connector given a test context."""

from abc import ABC, abstractmethod
from typing import Callable, Iterable, List

import asyncer
from dagger import Container
from pipelines.actions import environments, secrets
from pipelines.bases import Step, StepResult, StepStatus
from pipelines.builds import LOCAL_BUILD_PLATFORM
from pipelines.builds.python_connectors import BuildConnectorImage
from pipelines.contexts import ConnectorContext
from pipelines.tests.common import AcceptanceTests
from pipelines.utils import export_container_to_tarball


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


class PytestStep(Step, ABC):
    """An abstract class to run pytest tests and evaluate success or failure according to pytest logs."""

    PYTEST_INI_FILE_NAME = "pytest.ini"
    PYPROJECT_FILE_NAME = "pyproject.toml"
    extra_dependencies_names = ("dev", "tests")
    skipped_exit_code = 5

    @property
    @abstractmethod
    def test_directory_name(self) -> str:
        raise NotImplementedError("test_directory_name must be implemented in the child class.")

    async def _run(self, connector_under_test: Container) -> StepResult:
        """Run all pytest tests declared in the test directory of the connector code.

        Args:
            connector_under_test (Container): The connector under test container.

        Returns:
            StepResult: Failure or success of the unit tests with stdout and stdout.
        """
        if not await self.check_if_tests_are_available(self.test_directory_name):
            return self.skip(f"No {self.test_directory_name} directory found in the connector.")

        connector_under_test = connector_under_test.with_(await self.testing_environment(self.extra_dependencies_names))

        return await self.get_step_result(connector_under_test)

    async def check_if_tests_are_available(self, test_directory_name: str) -> bool:
        """Check if the tests are available in the connector directory.

        Returns:
            bool: True if the tests are available.
        """
        connector_dir = await self.context.get_connector_dir()
        connector_dir_entries = await connector_dir.entries()
        return test_directory_name in connector_dir_entries

    async def testing_environment(self, extra_dependencies_names: Iterable[str]) -> Callable:
        """Install all extra dependencies of a connector.

        Args:
            extra_dependencies_names (Iterable[str]): Extra dependencies to install.

        Returns:
            Callable: The decorator to use with the with_ method of a container.
        """
        secret_mounting_function = await environments.mounted_connector_secrets(self.context, "secrets")
        connector_dir = await self.context.get_connector_dir()
        connector_dir_entries = await connector_dir.entries()

        if self.PYTEST_INI_FILE_NAME in connector_dir_entries:
            config_file_name = self.PYTEST_INI_FILE_NAME
            test_config = await self.context.get_connector_dir(include=[self.PYTEST_INI_FILE_NAME]).file(self.PYTEST_INI_FILE_NAME)
            self.logger.info(f"Found {self.PYTEST_INI_FILE_NAME}, using it for testing.")
        elif self.PYPROJECT_FILE_NAME in connector_dir_entries:
            config_file_name = self.PYPROJECT_FILE_NAME
            test_config = await self.context.get_connector_dir(include=[self.PYTEST_INI_FILE_NAME]).file(self.PYTEST_INI_FILE_NAME)
            self.logger.info(f"Found {self.PYPROJECT_FILE_NAME} at connector level, using it for testing.")
        else:
            config_file_name = f"global_{self.PYPROJECT_FILE_NAME}"
            test_config = await self.context.get_repo_dir(include=[self.PYPROJECT_FILE_NAME]).file(self.PYPROJECT_FILE_NAME)
            self.logger.info(f"Found {self.PYPROJECT_FILE_NAME} at repo level, using it for testing.")

        def prepare_for_testing(built_connector_container: Container) -> Container:
            return (
                built_connector_container
                # Reset the entrypoint
                .with_entrypoint([])
                # Mount the connector directory in /test_environment
                # For build optimization the full directory is not mounted by default
                # We need the setup.py/pyproject.toml and the tests code to be available
                # Install the extra dependencies
                .with_mounted_directory("/test_environment", connector_dir)
                # Jump in the /test_environment directory
                .with_workdir("/test_environment").with_mounted_file(config_file_name, test_config)
                # Mount the secrets
                .with_(secret_mounting_function)
                # Install the extra dependencies
                .with_exec(["pip", "install", f".[{','.join(extra_dependencies_names)}]"], skip_entrypoint=True)
                # Execute pytest on the test directory
                .with_exec(
                    [
                        "python",
                        "-m",
                        "pytest",
                        "-s",
                        self.test_directory_name,
                        "-c",
                        config_file_name,
                    ]
                )
            )

        return prepare_for_testing


class UnitTests(PytestStep):
    """A step to run the connector unit tests with Pytest."""

    title = "Unit tests"
    test_directory_name = "unit_tests"


class IntegrationTests(PytestStep):
    """A step to run the connector integration tests with Pytest."""

    title = "Integration tests"
    test_directory_name = "integration_tests"


async def run_all_tests(context: ConnectorContext) -> List[StepResult]:
    """Run all tests for a Python connector.

    Args:
        context (ConnectorContext): The current connector context.

    Returns:
        List[StepResult]: The results of all the steps that ran or were skipped.
    """
    step_results = []
    build_connector_image_results = await BuildConnectorImage(context, LOCAL_BUILD_PLATFORM).run()
    if build_connector_image_results.status is StepStatus.FAILURE:
        return [build_connector_image_results]
    step_results.append(build_connector_image_results)

    connector_image_tar_file, _ = await export_container_to_tarball(context, build_connector_image_results.output_artifact)
    connector_container = build_connector_image_results.output_artifact

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
