#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module groups steps made to run tests for a specific Python connector given a test context."""

from abc import ABC, abstractmethod
from typing import Callable, Iterable, List, Tuple

import asyncer
import pipelines.dagger.actions.python.common
import pipelines.dagger.actions.system.docker
from dagger import Container, File
from pipelines.airbyte_ci.connectors.build_image.steps.python_connectors import BuildConnectorImages
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.airbyte_ci.connectors.test.steps.common import AcceptanceTests, CheckBaseImageIsUsed
from pipelines.consts import LOCAL_BUILD_PLATFORM
from pipelines.dagger.actions import secrets
from pipelines.models.steps import Step, StepResult, StepStatus


class PytestStep(Step, ABC):
    """An abstract class to run pytest tests and evaluate success or failure according to pytest logs."""

    PYTEST_INI_FILE_NAME = "pytest.ini"
    PYPROJECT_FILE_NAME = "pyproject.toml"
    common_test_dependencies: List[str] = []

    skipped_exit_code = 5
    bind_to_docker_host = False

    @property
    @abstractmethod
    def test_directory_name(self) -> str:
        raise NotImplementedError("test_directory_name must be implemented in the child class.")

    @property
    def extra_dependencies_names(self) -> Iterable[str]:
        if self.context.connector.is_using_poetry:
            return ("dev",)
        return ("dev", "tests")

    @property
    def additional_pytest_options(self) -> List[str]:
        """Theses options are added to the pytest command.

        Returns:
            List[str]: The additional pytest options.
        """
        return []

    async def _run(self, connector_under_test: Container) -> StepResult:
        """Run all pytest tests declared in the test directory of the connector code.

        Args:
            connector_under_test (Container): The connector under test container.

        Returns:
            StepResult: Failure or success of the unit tests with stdout and stdout.
        """
        if not await self.check_if_tests_are_available(self.test_directory_name):
            return self.skip(f"No {self.test_directory_name} directory found in the connector.")

        test_config_file_name, test_config_file = await self.get_config_file_name_and_file()
        test_environment = await self.install_testing_environment(
            connector_under_test, test_config_file_name, test_config_file, self.extra_dependencies_names
        )
        pytest_command = self.get_pytest_command(test_config_file_name)

        if self.bind_to_docker_host:
            test_environment = pipelines.dagger.actions.system.docker.with_bound_docker_host(self.context, test_environment)

        test_execution = test_environment.with_exec(pytest_command)

        return await self.get_step_result(test_execution)

    def get_pytest_command(self, test_config_file_name: str) -> List[str]:
        """Get the pytest command to run.

        Returns:
            List[str]: The pytest command to run.
        """
        cmd = ["pytest", "-s", self.test_directory_name, "-c", test_config_file_name] + self.additional_pytest_options
        if self.context.connector.is_using_poetry:
            return ["poetry", "run"] + cmd
        return cmd

    async def check_if_tests_are_available(self, test_directory_name: str) -> bool:
        """Check if the tests are available in the connector directory.

        Returns:
            bool: True if the tests are available.
        """
        connector_dir = await self.context.get_connector_dir()
        connector_dir_entries = await connector_dir.entries()
        return test_directory_name in connector_dir_entries

    async def get_config_file_name_and_file(self) -> Tuple[str, File]:
        """Get the config file name and file to use for pytest.

        The order of priority is:
        - pytest.ini file in the connector directory
        - pyproject.toml file in the connector directory
        - pyproject.toml file in the repository directory

        Returns:
            Tuple[str, File]: The config file name and file to use for pytest.
        """
        connector_dir = await self.context.get_connector_dir()
        connector_dir_entries = await connector_dir.entries()
        if self.PYTEST_INI_FILE_NAME in connector_dir_entries:
            config_file_name = self.PYTEST_INI_FILE_NAME
            test_config = (await self.context.get_connector_dir(include=[self.PYTEST_INI_FILE_NAME])).file(self.PYTEST_INI_FILE_NAME)
            self.logger.info(f"Found {self.PYTEST_INI_FILE_NAME}, using it for testing.")
        elif self.PYPROJECT_FILE_NAME in connector_dir_entries:
            config_file_name = self.PYPROJECT_FILE_NAME
            test_config = (await self.context.get_connector_dir(include=[self.PYPROJECT_FILE_NAME])).file(self.PYPROJECT_FILE_NAME)
            self.logger.info(f"Found {self.PYPROJECT_FILE_NAME} at connector level, using it for testing.")
        else:
            config_file_name = f"global_{self.PYPROJECT_FILE_NAME}"
            test_config = (await self.context.get_repo_dir(include=[self.PYPROJECT_FILE_NAME])).file(self.PYPROJECT_FILE_NAME)
            self.logger.info(f"Found {self.PYPROJECT_FILE_NAME} at repo level, using it for testing.")
        return config_file_name, test_config

    async def install_testing_environment(
        self,
        built_connector_container: Container,
        test_config_file_name: str,
        test_config_file: File,
        extra_dependencies_names: Iterable[str],
    ) -> Callable:
        """Install the connector with the extra dependencies in /test_environment.

        Args:
            extra_dependencies_names (Iterable[str]): Extra dependencies to install.

        Returns:
            Callable: The decorator to use with the with_ method of a container.
        """
        secret_mounting_function = await secrets.mounted_connector_secrets(self.context, "secrets")

        container_with_test_deps = (
            # Install the connector python package in /test_environment with the extra dependencies
            await pipelines.dagger.actions.python.common.with_python_connector_installed(
                self.context,
                # Reset the entrypoint to run non airbyte commands
                built_connector_container.with_entrypoint([]),
                str(self.context.connector.code_directory),
                additional_dependency_groups=extra_dependencies_names,
            )
        )
        if self.common_test_dependencies:
            container_with_test_deps = container_with_test_deps.with_exec(
                ["pip", "install", f'{" ".join(self.common_test_dependencies)}'], skip_entrypoint=True
            )
        return (
            container_with_test_deps
            # Mount the test config file
            .with_mounted_file(test_config_file_name, test_config_file)
            # Mount the secrets
            .with_(secret_mounting_function).with_env_variable("PYTHONPATH", ".")
        )


class UnitTests(PytestStep):
    """A step to run the connector unit tests with Pytest."""

    title = "Unit tests"
    test_directory_name = "unit_tests"
    common_test_dependencies = ["pytest-cov==4.1.0"]
    MINIMUM_COVERAGE_FOR_CERTIFIED_CONNECTORS = 90

    @property
    def additional_pytest_options(self) -> List[str]:
        """Make sure the coverage computation is run for the unit tests.
        Fail if the coverage is under 90% for certified connectors.

        Returns:
            List[str]: The additional pytest options to run coverage reports.
        """
        coverage_options = ["--cov", self.context.connector.technical_name.replace("-", "_")]
        if self.context.connector.support_level == "certified":
            coverage_options += ["--cov-fail-under", str(self.MINIMUM_COVERAGE_FOR_CERTIFIED_CONNECTORS)]

        return super().additional_pytest_options + coverage_options


class IntegrationTests(PytestStep):
    """A step to run the connector integration tests with Pytest."""

    title = "Integration tests"
    test_directory_name = "integration_tests"
    bind_to_docker_host = True


async def run_all_tests(context: ConnectorContext) -> List[StepResult]:
    """Run all tests for a Python connector.

    Args:
        context (ConnectorContext): The current connector context.

    Returns:
        List[StepResult]: The results of all the steps that ran or were skipped.
    """
    step_results = []
    build_connector_image_results = await BuildConnectorImages(context, LOCAL_BUILD_PLATFORM).run()
    if build_connector_image_results.status is StepStatus.FAILURE:
        return [build_connector_image_results]
    step_results.append(build_connector_image_results)

    connector_container = build_connector_image_results.output_artifact[LOCAL_BUILD_PLATFORM]

    context.connector_secrets = await secrets.get_connector_secrets(context)

    unit_test_results = await UnitTests(context).run(connector_container)

    if unit_test_results.status is StepStatus.FAILURE:
        return step_results + [unit_test_results]
    step_results.append(unit_test_results)
    async with asyncer.create_task_group() as task_group:
        tasks = [
            task_group.soonify(IntegrationTests(context).run)(connector_container),
            task_group.soonify(AcceptanceTests(context, context.concurrent_cat).run)(connector_container),
            task_group.soonify(CheckBaseImageIsUsed(context).run)(),
        ]

    return step_results + [task.value for task in tasks]
