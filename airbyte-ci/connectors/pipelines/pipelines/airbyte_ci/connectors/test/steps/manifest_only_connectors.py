#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
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
    common_test_dependencies = ["pytest"]

    async def install_testing_environment(
        self,
        built_connector_container: Container,
        test_config_file_name: str,
        test_config_file: File,
        extra_dependencies_names: Sequence[str],
    ) -> Container:
        """Install the testing environment for manifest-only connectors."""

        connector_name = self.context.connector.technical_name
        connector_path = f"/airbyte-integrations/connectors/{connector_name}"

        # Create a symlink between the local connector's directory and the built container
        test_environment = built_connector_container.with_workdir(f"{connector_path}/unit_tests").with_exec(
            ["ln", "-s", "/source-declarative-manifest", connector_path]
        )

        return await super().install_testing_environment(
            test_environment,
            test_config_file_name,
            test_config_file,
            extra_dependencies_names,
        )

    async def get_config_file_name_and_file(self) -> Tuple[str, File]:
        """
        Get the config file name and file to use for pytest.
        For manifest-only connectors, we expect the poetry config to be found in the unit_tests directory.
        """
        connector_name = self.context.connector.technical_name
        connector_dir = await self.context.get_connector_dir()
        unit_tests_dir = connector_dir.directory("unit_tests")
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
        cmd = ["pytest", "-s", self.test_directory_name, "-c", test_config_file_name] + self.params_as_cli_options
        return ["poetry", "run"] + cmd
