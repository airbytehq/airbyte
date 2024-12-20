#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module groups steps made to run tests for a specific Python connector given a test context."""

from abc import ABC, abstractmethod
from typing import List, Sequence, Tuple

import dpath.util
from dagger import Container, File

import pipelines.dagger.actions.python.common
import pipelines.dagger.actions.system.docker
from pipelines import hacks
from pipelines.airbyte_ci.connectors.build_image.steps.python_connectors import BuildConnectorImages
from pipelines.airbyte_ci.connectors.consts import CONNECTOR_TEST_STEP_ID
from pipelines.airbyte_ci.connectors.test.context import ConnectorTestContext
from pipelines.airbyte_ci.connectors.test.steps.common import AcceptanceTests, IncrementalAcceptanceTests, LiveTests
from pipelines.consts import LOCAL_BUILD_PLATFORM
from pipelines.dagger.actions import secrets
from pipelines.dagger.actions.python.poetry import with_poetry
from pipelines.helpers.execution.run_steps import STEP_TREE, StepToRun
from pipelines.helpers.utils import raise_if_not_user
from pipelines.models.steps import STEP_PARAMS, Step, StepResult

# Pin the PyAirbyte version to avoid updates from breaking CI
PYAIRBYTE_VERSION = "0.20.2"


class PytestStep(Step, ABC):
    """An abstract class to run pytest tests and evaluate success or failure according to pytest logs."""

    context: ConnectorTestContext

    PYTEST_INI_FILE_NAME = "pytest.ini"
    PYPROJECT_FILE_NAME = "pyproject.toml"
    common_test_dependencies: List[str] = []

    skipped_exit_code = 5
    bind_to_docker_host = False
    accept_extra_params = True

    @property
    def default_params(self) -> STEP_PARAMS:
        """Default pytest options.

        Returns:
            dict: The default pytest options.
        """
        return super().default_params | {
            "-s": [],  # Disable capturing stdout/stderr in pytest
        }

    @property
    @abstractmethod
    def test_directory_name(self) -> str:
        raise NotImplementedError("test_directory_name must be implemented in the child class.")

    @property
    def extra_dependencies_names(self) -> Sequence[str]:
        if self.context.connector.is_using_poetry:
            return ("dev",)
        return ("dev", "tests")

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
        cmd = ["pytest", self.test_directory_name, "-c", test_config_file_name] + self.params_as_cli_options
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
        extra_dependencies_names: Sequence[str],
    ) -> Container:
        """Install the connector with the extra dependencies in /test_environment.

        Args:
            extra_dependencies_names (List[str]): Extra dependencies to install.

        Returns:
            Container: The container with the test environment installed.
        """
        user = await BuildConnectorImages.get_image_user(built_connector_container)
        secret_mounting_function = await secrets.mounted_connector_secrets(self.context, "secrets", self.secrets, owner=user)

        container_with_test_deps = (
            # Install the connector python package in /test_environment with the extra dependencies
            await pipelines.dagger.actions.python.common.with_python_connector_installed(
                self.context,
                # Reset the entrypoint to run non airbyte commands
                built_connector_container.with_entrypoint([]),
                str(self.context.connector.code_directory),
                user,
                additional_dependency_groups=extra_dependencies_names,
            )
        )
        if self.common_test_dependencies:
            container_with_test_deps = container_with_test_deps.with_user("root").with_exec(
                ["pip", "install", f'{" ".join(self.common_test_dependencies)}']
            )

        container_with_test_deps = (
            container_with_test_deps
            # Mount the test config file
            .with_mounted_file(test_config_file_name, test_config_file, owner=user)
            # Mount the secrets
            .with_(secret_mounting_function)
            .with_env_variable("PYTHONPATH", ".")
            # Make sure all files that were created or mounted under /airbyte are owned by the user
            .with_user("root")
            .with_exec(["chown", "-R", f"{user}:{user}", "/airbyte"])
            .with_user(user)
        )

        await raise_if_not_user(container_with_test_deps, user)
        return container_with_test_deps


class UnitTests(PytestStep):
    """A step to run the connector unit tests with Pytest."""

    title = "Unit tests"
    test_directory_name = "unit_tests"

    common_test_dependencies = ["pytest-cov==4.1.0"]
    MINIMUM_COVERAGE_FOR_CERTIFIED_CONNECTORS = 90

    @property
    def default_params(self) -> STEP_PARAMS:
        """Make sure the coverage computation is run for the unit tests.

        Returns:
            dict: The default pytest options.
        """
        coverage_options = {"--cov": [self.context.connector.technical_name.replace("-", "_")]}
        if self.context.connector.support_level == "certified":
            coverage_options["--cov-fail-under"] = [str(self.MINIMUM_COVERAGE_FOR_CERTIFIED_CONNECTORS)]
        return super().default_params | coverage_options


class PyAirbyteValidation(Step):
    """Validate the connector can be installed and invoked via Python, using PyAirbyte.

    When this fails, it generally signals that the connector is not installable or not
    runnable in a Python environment. The most common reasons for this are:
    1. Conflicting dependencies.
    2. Missing dependency declarations.
    3. Incorrect or invalid CLI entrypoints.
    """

    title = "Python CLI smoke test using PyAirbyte"

    context: ConnectorTestContext

    async def _run(self, connector_under_test: Container) -> StepResult:
        """Run all pytest tests declared in the test directory of the connector code.
        Args:
            connector_under_test (Container): The connector under test container.
        Returns:
            StepResult: Failure or success of the unit tests with stdout and stdout.
        """
        if dpath.util.get(self.context.connector.metadata, "remoteRegistries/pypi/enabled", default=False) is False:
            return self.skip("Connector is not flagged for PyPI publish, skipping Python CLI validation.")

        test_environment = await self.install_testing_environment(with_poetry(self.context))
        test_execution = test_environment.with_(
            hacks.never_fail_exec(
                [
                    "pyab",
                    "validate",
                    f"--connector={self.context.connector.technical_name}",
                    "--pip-url='.'",
                ]
            )
        )

        return await self.get_step_result(test_execution)

    async def install_testing_environment(
        self,
        built_connector_container: Container,
    ) -> Container:
        """Add PyAirbyte and secrets to the test environment."""
        context: ConnectorTestContext = self.context

        container_with_test_deps = await pipelines.dagger.actions.python.common.with_python_package(
            self.context, built_connector_container.with_entrypoint([]), str(context.connector.code_directory)
        )
        return container_with_test_deps.with_exec(["pip", "install", f"airbyte=={PYAIRBYTE_VERSION}"], use_entrypoint=True)


class IntegrationTests(PytestStep):
    """A step to run the connector integration tests with Pytest."""

    title = "Integration tests"
    test_directory_name = "integration_tests"

    bind_to_docker_host = True


def get_test_steps(context: ConnectorTestContext) -> STEP_TREE:
    """
    Get all the tests steps for a Python connector.
    """

    return [
        [StepToRun(id=CONNECTOR_TEST_STEP_ID.BUILD, step=BuildConnectorImages(context))],
        [
            StepToRun(
                id=CONNECTOR_TEST_STEP_ID.UNIT,
                step=UnitTests(context, secrets=context.get_secrets_for_step_id(CONNECTOR_TEST_STEP_ID.UNIT)),
                args=lambda results: {"connector_under_test": results[CONNECTOR_TEST_STEP_ID.BUILD].output[LOCAL_BUILD_PLATFORM]},
                depends_on=[CONNECTOR_TEST_STEP_ID.BUILD],
            )
        ],
        [
            StepToRun(
                id=CONNECTOR_TEST_STEP_ID.INTEGRATION,
                step=IntegrationTests(context, secrets=context.get_secrets_for_step_id(CONNECTOR_TEST_STEP_ID.INTEGRATION)),
                args=lambda results: {"connector_under_test": results[CONNECTOR_TEST_STEP_ID.BUILD].output[LOCAL_BUILD_PLATFORM]},
                depends_on=[CONNECTOR_TEST_STEP_ID.BUILD],
            ),
            StepToRun(
                id=CONNECTOR_TEST_STEP_ID.PYTHON_CLI_VALIDATION,
                step=PyAirbyteValidation(context),
                args=lambda results: {"connector_under_test": results[CONNECTOR_TEST_STEP_ID.BUILD].output[LOCAL_BUILD_PLATFORM]},
                depends_on=[CONNECTOR_TEST_STEP_ID.BUILD],
            ),
            StepToRun(
                id=CONNECTOR_TEST_STEP_ID.ACCEPTANCE,
                step=AcceptanceTests(
                    context,
                    concurrent_test_run=context.concurrent_cat,
                    secrets=context.get_secrets_for_step_id(CONNECTOR_TEST_STEP_ID.ACCEPTANCE),
                ),
                args=lambda results: {"connector_under_test_container": results[CONNECTOR_TEST_STEP_ID.BUILD].output[LOCAL_BUILD_PLATFORM]},
                depends_on=[CONNECTOR_TEST_STEP_ID.BUILD],
            ),
            StepToRun(
                id=CONNECTOR_TEST_STEP_ID.CONNECTOR_LIVE_TESTS,
                step=LiveTests(context),
                args=lambda results: {"connector_under_test_container": results[CONNECTOR_TEST_STEP_ID.BUILD].output[LOCAL_BUILD_PLATFORM]},
                depends_on=[CONNECTOR_TEST_STEP_ID.BUILD],
            ),
        ],
        [
            StepToRun(
                id=CONNECTOR_TEST_STEP_ID.INCREMENTAL_ACCEPTANCE,
                step=IncrementalAcceptanceTests(context, secrets=context.get_secrets_for_step_id(CONNECTOR_TEST_STEP_ID.ACCEPTANCE)),
                args=lambda results: {"current_acceptance_tests_result": results[CONNECTOR_TEST_STEP_ID.ACCEPTANCE]},
                depends_on=[CONNECTOR_TEST_STEP_ID.ACCEPTANCE],
            )
        ],
    ]
