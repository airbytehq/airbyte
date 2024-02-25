#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module groups steps made to run regression tests for any Source connector."""

import sys
from typing import List

import dagger
from dagger import Container, Directory
from pipelines import hacks
from pipelines.airbyte_ci.connectors.build_image.steps.python_connectors import BuildConnectorImages
from pipelines.airbyte_ci.connectors.consts import CONNECTOR_TEST_STEP_ID
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.airbyte_ci.connectors.test.steps.common import AcceptanceTests
from pipelines.consts import LOCAL_BUILD_PLATFORM
from pipelines.helpers.execution.run_steps import STEP_TREE, StepToRun
from pipelines.models.steps import StepResult, StepStatus

_BASE_CONTAINER_DIRECTORY = "/tmp"
_CONTAINER_TEST_OUTPUT_DIRECTORY = f"{_BASE_CONTAINER_DIRECTORY}/test_output"
_CONTAINER_EXPECTED_RECORDS_DIRECTORY = f"{_CONTAINER_TEST_OUTPUT_DIRECTORY}/expected_records"
_CONTAINER_ACCEPTANCE_TEST_CONFIG_FILEPATH = f"{_BASE_CONTAINER_DIRECTORY}/updated-acceptance-test-config.yml"
_HOST_TEST_OUTPUT_DIRECTORY = "/tmp/test_dir"
_REGRESSION_TEST_DIRECTORY = "/app/connector_acceptance_test/utils/regression_test.py"


class BuildConnectorImagesControl(BuildConnectorImages):
    @property
    def title(self):
        return f"{super().title}: Control Container ({self.docker_image_name})"


class BuildConnectorImagesTarget(BuildConnectorImages):
    @property
    def title(self):
        return f"{super().title}: Target Container ({self.docker_image_name})"


class RegressionTestsControl(AcceptanceTests):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._container_id_filepath = f"{_BASE_CONTAINER_DIRECTORY}/control_container_id.txt"

    @property
    def title(self):
        return f"Regression Tests: Control Container ({self.context.versions_to_test[0]})"

    async def get_cat_command(self, connector_dir: Directory) -> List[str]:
        return await super().get_cat_command(connector_dir) + [
            "--store-expected-records",
            _CONTAINER_EXPECTED_RECORDS_DIRECTORY,
            "--container-id-filepath",
            self._container_id_filepath,
        ]

    async def _run(self, connector_under_test_container: Container) -> StepResult:
        """Run the first phase of the regression test suite on a connector image.

        This phase runs connector acceptance tests on the connector and stores the output records which will
        be passed to the target container for expected record validation.

        Args:
            connector_under_test_container (Container): The container holding the connector under test image.

        Returns:
            StepResult: Failure or success of the acceptances tests with stdout and stderr.
        """
        if not self.context.connector.acceptance_test_config:
            return StepResult(step=self, status=StepStatus.SKIPPED)

        connector_dir = await self.context.get_connector_dir()
        cat_container = await self._build_connector_acceptance_test(connector_under_test_container, connector_dir)
        cat_command = await self.get_cat_command(connector_dir)

        # Execute CATs and prepare for the target run by exporting output to a directory on the host
        cat_container = await cat_container.with_(hacks.never_fail_exec(cat_command))
        await cat_container.directory(_BASE_CONTAINER_DIRECTORY).export(_HOST_TEST_OUTPUT_DIRECTORY)

        await self._update_secrets_dir(cat_container)
        return await self.get_step_result(cat_container)


class RegressionTestsTarget(AcceptanceTests):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._container_id_filepath = f"{_BASE_CONTAINER_DIRECTORY}/target_container_id.txt"

    @property
    def title(self):
        return f"Regression Tests: Target Container ({self.context.versions_to_test[1]})"

    async def get_cat_command(self, connector_dir: Directory) -> List[str]:
        return await super().get_cat_command(connector_dir) + [
            "--acceptance-test-config-filepath",
            _CONTAINER_ACCEPTANCE_TEST_CONFIG_FILEPATH,
            "--container-id-filepath",
            self._container_id_filepath,
        ]

    async def _run(self, connector_under_test_container: Container) -> StepResult:
        """Run the second phase of the regression test suite on a connector image.

        This phase runs connector acceptance tests on the connector, using the records output by the run of the
         control container as expected records.

        Args:
            connector_under_test_container (Container): The container holding the connector under test image.

        Returns:
            StepResult: Failure or success of the acceptances tests with stdout and stderr.
        """
        if not self.context.connector.acceptance_test_config:
            return StepResult(step=self, status=StepStatus.SKIPPED)

        connector_dir = await self.context.get_connector_dir()
        cat_container = await self._build_connector_acceptance_test(connector_under_test_container, connector_dir)
        cat_command = await self.get_cat_command(connector_dir)

        # Prepare the host container with an acceptance-test-config.yml whose expected records location points to the
        # mounted directory containing the records output from the control run.
        prep_container = await self._prepare_regression_test(cat_container)
        await prep_container.directory(_BASE_CONTAINER_DIRECTORY).export(_HOST_TEST_OUTPUT_DIRECTORY)
        prep_result = await self.get_step_result(prep_container)
        if not prep_result.success:
            return prep_result

        async with dagger.Connection(dagger.Config(log_output=sys.stderr)) as client:
            # Give the target container access to the output from the RegressionTestsControl phase and then execute CATs
            temp_dir = client.host().directory(_HOST_TEST_OUTPUT_DIRECTORY)
            cat_container = await cat_container.with_directory(_BASE_CONTAINER_DIRECTORY, temp_dir)
            cat_container = cat_container.with_(hacks.never_fail_exec(cat_command))

        await self._update_secrets_dir(cat_container)
        return await self.get_step_result(cat_container)

    async def _prepare_regression_test(self, cat_container: Container) -> Container:
        rewrite_config_command = [
            "python",
            _REGRESSION_TEST_DIRECTORY,
            ".",
            _CONTAINER_ACCEPTANCE_TEST_CONFIG_FILEPATH,
            _CONTAINER_EXPECTED_RECORDS_DIRECTORY,
        ]
        return await cat_container.with_(hacks.never_fail_exec(rewrite_config_command))


def get_test_steps(context: ConnectorContext) -> STEP_TREE:
    """
    Get all the tests steps for running regression tests.
    """
    control_image, target_image = context.versions_to_test

    return [
        [
            StepToRun(
                id=CONNECTOR_TEST_STEP_ID.REGRESSION_TEST_BUILD_CONTROL,
                step=BuildConnectorImagesControl(context, docker_image_name=control_image),
            ),
        ],
        [
            StepToRun(
                id=CONNECTOR_TEST_STEP_ID.REGRESSION_TEST_CONTROL,
                step=RegressionTestsControl(context, context.concurrent_cat),
                args=lambda results: {
                    "connector_under_test_container": results[CONNECTOR_TEST_STEP_ID.REGRESSION_TEST_BUILD_CONTROL].output_artifact[
                        LOCAL_BUILD_PLATFORM
                    ]
                },
                depends_on=[CONNECTOR_TEST_STEP_ID.REGRESSION_TEST_BUILD_CONTROL],
            ),
        ],
        [
            StepToRun(
                id=CONNECTOR_TEST_STEP_ID.REGRESSION_TEST_BUILD_TARGET,
                step=BuildConnectorImagesTarget(context, docker_image_name=target_image),
                depends_on=[CONNECTOR_TEST_STEP_ID.REGRESSION_TEST_CONTROL],
            )
        ],
        [
            StepToRun(
                id=CONNECTOR_TEST_STEP_ID.REGRESSION_TEST_TARGET,
                step=RegressionTestsTarget(context, context.concurrent_cat),
                args=lambda results: {
                    "connector_under_test_container": results[CONNECTOR_TEST_STEP_ID.REGRESSION_TEST_BUILD_TARGET].output_artifact[
                        LOCAL_BUILD_PLATFORM
                    ]
                },
                depends_on=[CONNECTOR_TEST_STEP_ID.REGRESSION_TEST_BUILD_TARGET, CONNECTOR_TEST_STEP_ID.REGRESSION_TEST_CONTROL],
            )
        ],
    ]
