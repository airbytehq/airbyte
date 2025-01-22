#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module groups steps made to run tests for a specific Java connector given a test context."""

from __future__ import annotations

from typing import TYPE_CHECKING

import anyio
from dagger import File, QueryError

from pipelines.airbyte_ci.connectors.build_image.steps.java_connectors import (
    BuildConnectorDistributionTar,
    BuildConnectorImages,
    dist_tar_directory_path,
)
from pipelines.airbyte_ci.connectors.build_image.steps.normalization import BuildOrPullNormalization
from pipelines.airbyte_ci.connectors.consts import CONNECTOR_TEST_STEP_ID
from pipelines.airbyte_ci.connectors.test.context import ConnectorTestContext
from pipelines.airbyte_ci.connectors.test.steps.common import AcceptanceTests
from pipelines.airbyte_ci.steps.gradle import GradleTask
from pipelines.consts import LOCAL_BUILD_PLATFORM
from pipelines.dagger.actions.system import docker
from pipelines.helpers.execution.run_steps import StepToRun
from pipelines.helpers.utils import export_container_to_tarball
from pipelines.models.steps import STEP_PARAMS, StepResult, StepStatus

if TYPE_CHECKING:
    from typing import Callable, Dict, List, Optional

    from pipelines.helpers.execution.run_steps import RESULTS_DICT, STEP_TREE


class IntegrationTests(GradleTask):
    """A step to run integrations tests for Java connectors using the integrationTestJava Gradle task."""

    title = "Java Connector Integration Tests"
    gradle_task_name = "integrationTestJava"
    mount_connector_secrets = True
    bind_to_docker_host = True
    with_test_artifacts = True

    @property
    def default_params(self) -> STEP_PARAMS:
        return super().default_params | {
            # Exclude the assemble task to avoid a circular dependency on airbyte-ci.
            # The integrationTestJava gradle task depends on assemble, which in turns
            # depends on buildConnectorImage to build the connector's docker image.
            # At this point, the docker image has already been built.
            "-x": ["assemble"],
        }

    async def _load_normalization_image(self, normalization_tar_file: File) -> None:
        normalization_image_tag = f"{self.context.connector.normalization_repository}:dev"
        self.context.logger.info("Load the normalization image to the docker host.")
        await docker.load_image_to_docker_host(self.context, normalization_tar_file, normalization_image_tag)
        self.context.logger.info("Successfully loaded the normalization image to the docker host.")

    async def _load_connector_image(self, connector_tar_file: File) -> None:
        connector_image_tag = f"airbyte/{self.context.connector.technical_name}:dev"
        self.context.logger.info("Load the connector image to the docker host")
        await docker.load_image_to_docker_host(self.context, connector_tar_file, connector_image_tag)
        self.context.logger.info("Successfully loaded the connector image to the docker host.")

    async def _run(self, connector_tar_file: File, normalization_tar_file: Optional[File]) -> StepResult:
        try:
            async with anyio.create_task_group() as tg:
                if normalization_tar_file:
                    tg.start_soon(self._load_normalization_image, normalization_tar_file)
                tg.start_soon(self._load_connector_image, connector_tar_file)
        except QueryError as e:
            return StepResult(step=self, status=StepStatus.FAILURE, stderr=str(e))
        # Run the gradle integration test task now that the required docker images have been loaded.
        return await super()._run()


class UnitTests(GradleTask):
    """A step to run unit tests for Java connectors."""

    title = "Java Connector Unit Tests"
    gradle_task_name = "test"
    bind_to_docker_host = True
    with_test_artifacts = True


def _create_integration_step_args_factory(context: ConnectorTestContext) -> Callable:
    """
    Create a function that can process the args for the integration step.
    """

    async def _create_integration_step_args(results: RESULTS_DICT) -> Dict[str, Optional[File]]:
        connector_container = results["build"].output[LOCAL_BUILD_PLATFORM]
        connector_image_tar_file, _ = await export_container_to_tarball(context, connector_container, LOCAL_BUILD_PLATFORM)

        if context.connector.supports_normalization:
            tar_file_name = f"{context.connector.normalization_repository}_{context.git_revision}.tar"
            build_normalization_results = results["build_normalization"]

            normalization_container = build_normalization_results.output
            normalization_tar_file, _ = await export_container_to_tarball(
                context, normalization_container, LOCAL_BUILD_PLATFORM, tar_file_name=tar_file_name
            )
        else:
            normalization_tar_file = None

        return {"connector_tar_file": connector_image_tar_file, "normalization_tar_file": normalization_tar_file}

    return _create_integration_step_args


def _get_normalization_steps(context: ConnectorTestContext) -> List[StepToRun]:
    normalization_image = f"{context.connector.normalization_repository}:dev"
    context.logger.info(f"This connector supports normalization: will build {normalization_image}.")
    normalization_steps = [
        StepToRun(
            id=CONNECTOR_TEST_STEP_ID.BUILD_NORMALIZATION,
            step=BuildOrPullNormalization(context, normalization_image, LOCAL_BUILD_PLATFORM),
            depends_on=[CONNECTOR_TEST_STEP_ID.BUILD],
        )
    ]

    return normalization_steps


def _get_acceptance_test_steps(context: ConnectorTestContext) -> List[StepToRun]:
    """
    Generate the steps to run the acceptance tests for a Java connector.
    """

    # Run tests in parallel
    return [
        StepToRun(
            id=CONNECTOR_TEST_STEP_ID.INTEGRATION,
            step=IntegrationTests(context, secrets=context.get_secrets_for_step_id(CONNECTOR_TEST_STEP_ID.INTEGRATION)),
            args=_create_integration_step_args_factory(context),
            depends_on=[CONNECTOR_TEST_STEP_ID.BUILD],
        ),
        StepToRun(
            id=CONNECTOR_TEST_STEP_ID.ACCEPTANCE,
            step=AcceptanceTests(
                context, secrets=context.get_secrets_for_step_id(CONNECTOR_TEST_STEP_ID.ACCEPTANCE), concurrent_test_run=False
            ),
            args=lambda results: {"connector_under_test_container": results[CONNECTOR_TEST_STEP_ID.BUILD].output[LOCAL_BUILD_PLATFORM]},
            depends_on=[CONNECTOR_TEST_STEP_ID.BUILD],
        ),
    ]


def get_test_steps(context: ConnectorTestContext) -> STEP_TREE:
    """
    Get all the tests steps for a Java connector.
    """

    steps: STEP_TREE = [
        [StepToRun(id=CONNECTOR_TEST_STEP_ID.BUILD_TAR, step=BuildConnectorDistributionTar(context))],
        [
            StepToRun(
                id=CONNECTOR_TEST_STEP_ID.UNIT,
                step=UnitTests(context, secrets=context.get_secrets_for_step_id(CONNECTOR_TEST_STEP_ID.UNIT)),
                depends_on=[CONNECTOR_TEST_STEP_ID.BUILD_TAR],
            )
        ],
        [
            StepToRun(
                id=CONNECTOR_TEST_STEP_ID.BUILD,
                step=BuildConnectorImages(context),
                args=lambda results: {"dist_dir": results[CONNECTOR_TEST_STEP_ID.BUILD_TAR].output.directory("build/distributions")},
                depends_on=[CONNECTOR_TEST_STEP_ID.BUILD_TAR],
            ),
        ],
    ]

    if context.connector.supports_normalization:
        normalization_steps = _get_normalization_steps(context)
        steps.append(normalization_steps)

    acceptance_test_steps = _get_acceptance_test_steps(context)
    steps.append(acceptance_test_steps)

    return steps
