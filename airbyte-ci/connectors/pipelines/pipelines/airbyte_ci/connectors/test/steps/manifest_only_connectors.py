#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

"""This module groups steps made to run tests for a specific manifest only connector given a test context."""

from typing import List, Sequence, Tuple

from dagger import Container, File

from pipelines.airbyte_ci.connectors.build_image.steps.manifest_only_connectors import BuildConnectorImages
from pipelines.airbyte_ci.connectors.consts import CONNECTOR_TEST_STEP_ID
from pipelines.airbyte_ci.connectors.test.context import ConnectorTestContext
from pipelines.airbyte_ci.connectors.test.steps.common import AcceptanceTests, IncrementalAcceptanceTests, LiveTests
from pipelines.airbyte_ci.connectors.test.steps.python_connectors import PytestStep
from pipelines.consts import LOCAL_BUILD_PLATFORM
from pipelines.dagger.actions import secrets
from pipelines.helpers.execution.run_steps import STEP_TREE, StepToRun


def get_test_steps(context: ConnectorTestContext) -> STEP_TREE:
    """
    Get all the tests steps for a Python connector.
    """

    return [
        [StepToRun(id=CONNECTOR_TEST_STEP_ID.BUILD, step=BuildConnectorImages(context))],
        [
            StepToRun(
                id=CONNECTOR_TEST_STEP_ID.UNIT,
                step=ManifestOnlyConnectorUnitTests(context),
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


class ManifestOnlyConnectorUnitTests(PytestStep):
    """A step to run unit tests for a manifest-only connector"""

    title = "Manifest-only unit tests"
    test_directory_name = "unit_tests"
    common_test_dependencies = ["freezegun", "pytest", "pytest-mock", "requests-mock"]

    async def install_testing_environment(
        self,
        built_connector_container: Container,
        test_config_file_name: str,
        test_config_file: File,
        extra_dependencies_names: Sequence[str],
    ) -> Container:
        """Install the testing environment for manifest-only connectors."""

        connector_name = self.context.connector.technical_name
        # Use a simpler path structure to match what the CDK expects
        test_dir = "/tmp/test_environment"
        connector_base_path = f"{test_dir}/airbyte-integrations/connectors"
        connector_path = f"{connector_base_path}/{connector_name}"

        # Get the proper user from the container
        user = await built_connector_container.user()
        if not user:
            user = "root"

        # Set up base test environment with reset entrypoint
        test_environment = built_connector_container.with_entrypoint([])

        # Create test directories with proper permissions
        test_environment = (
            test_environment.with_user("root")  # Temporarily switch to root to create directories
            .with_exec(["mkdir", "-p", test_dir, connector_base_path, connector_path, f"{connector_path}/{self.test_directory_name}"])
            .with_workdir(test_dir)
        )

        # Mount the connector directory and files
        connector_dir = await self.context.get_connector_dir()

        # Check what files are in the connector directory to identify components.py
        connector_entries = await connector_dir.entries()
        self.logger.info(f"Files in connector directory: {connector_entries}")

        # Mount the entire connector directory to ensure all files (especially components.py) are available
        test_environment = test_environment.with_mounted_directory(connector_path, connector_dir)

        # Get and mount the unit_tests directory specifically
        unit_tests_dir = connector_dir.directory(self.test_directory_name)
        unit_tests_path = f"{connector_path}/{self.test_directory_name}"

        # Mount secrets
        secret_mounting_function = await secrets.mounted_connector_secrets(self.context, f"{test_dir}/secrets", self.secrets, owner=user)

        # Apply secrets and set up Python path
        test_environment = test_environment.with_(secret_mounting_function).with_env_variable(
            "PYTHONPATH", f"{connector_base_path}:{connector_path}:{unit_tests_path}:{test_dir}"
        )

        # Create symlink to source-declarative-manifest
        test_environment = test_environment.with_exec(["ln", "-s", "/source-declarative-manifest", connector_path])

        # Set working directory to unit tests path
        test_environment = test_environment.with_workdir(unit_tests_path)

        # Install Poetry
        test_environment = test_environment.with_exec(["echo", "=== INSTALLING POETRY ==="]).with_exec(["pip", "install", "poetry"])

        # Install dependencies directly with Poetry
        test_environment = test_environment.with_exec(
            ["poetry", "config", "virtualenvs.create", "false"]  # Disable virtualenv creation
        ).with_exec(
            ["poetry", "install", "--no-root"]  # Install dependencies without the root package
        )

        # Install common test dependencies. This shouldn't be needed as we're now
        # using the connector's pyproject.toml, but it's here to support MO connectors
        # that might have dependencies not listed in the pyproject.toml.
        if self.common_test_dependencies:
            test_environment = test_environment.with_exec(["echo", "=== INSTALLING COMMON TEST DEPENDENCIES ==="]).with_exec(
                ["pip", "install"] + self.common_test_dependencies
            )

        # Set ownership of all files to the proper user and switch to that user
        test_environment = test_environment.with_exec(["chown", "-R", f"{user}:{user}", test_dir]).with_user(user)

        return test_environment

    async def get_config_file_name_and_file(self) -> Tuple[str, File]:
        """
        Get the config file name and file to use for pytest.
        For manifest-only connectors, we expect the poetry config to be found
        in the unit_tests directory.
        """
        connector_name = self.context.connector.technical_name
        connector_dir = await self.context.get_connector_dir()
        unit_tests_dir = connector_dir.directory(self.test_directory_name)
        unit_tests_entries = await unit_tests_dir.entries()
        if self.PYPROJECT_FILE_NAME in unit_tests_entries:
            config_file_name = self.PYPROJECT_FILE_NAME
            test_config = unit_tests_dir.file(self.PYPROJECT_FILE_NAME)
            self.logger.info(f"Found {self.PYPROJECT_FILE_NAME} in the unit_tests directory for {connector_name}, using it for testing.")
            return config_file_name, test_config
        else:
            raise FileNotFoundError(f"Could not find {self.PYPROJECT_FILE_NAME} in the unit_tests directory for {connector_name}.")

    def get_pytest_command(self, test_config_file_name: str) -> List[str]:
        """Get the pytest command to run."""
        cmd = ["pytest", "-v", ".", "-c", test_config_file_name] + self.params_as_cli_options
        return ["poetry", "run"] + cmd
