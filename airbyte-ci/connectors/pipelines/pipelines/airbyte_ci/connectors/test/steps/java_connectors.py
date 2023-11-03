#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module groups steps made to run tests for a specific Java connector given a test context."""

from typing import List, Optional

import anyio
import asyncer
from dagger import Directory, File, QueryError
from pipelines.airbyte_ci.connectors.build_image.steps.java_connectors import (
    BuildConnectorDistributionTar,
    BuildConnectorImages,
    dist_tar_directory_path,
)
from pipelines.airbyte_ci.connectors.build_image.steps.normalization import BuildOrPullNormalization
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.airbyte_ci.connectors.test.steps.common import AcceptanceTests
from pipelines.airbyte_ci.steps.gradle import GradleTask
from pipelines.consts import LOCAL_BUILD_PLATFORM
from pipelines.dagger.actions import secrets
from pipelines.dagger.actions.system import docker
from pipelines.helpers.run_steps import StepToRun
from pipelines.helpers.utils import export_container_to_tarball
from pipelines.models.steps import StepResult, StepStatus


class IntegrationTests(GradleTask):
    """A step to run integrations tests for Java connectors using the integrationTestJava Gradle task."""

    title = "Java Connector Integration Tests"
    gradle_task_name = "integrationTestJava -x buildConnectorImage -x assemble"
    mount_connector_secrets = True
    bind_to_docker_host = True

    async def _load_normalization_image(self, normalization_tar_file: File):
        normalization_image_tag = f"{self.context.connector.normalization_repository}:dev"
        self.context.logger.info("Load the normalization image to the docker host.")
        await docker.load_image_to_docker_host(self.context, normalization_tar_file, normalization_image_tag)
        self.context.logger.info("Successfully loaded the normalization image to the docker host.")

    async def _load_connector_image(self, connector_tar_file: File):
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
            return StepResult(self, StepStatus.FAILURE, stderr=str(e))
        # Run the gradle integration test task now that the required docker images have been loaded.
        return await super()._run()


class UnitTests(GradleTask):
    """A step to run unit tests for Java connectors."""

    title = "Java Connector Unit Tests"
    gradle_task_name = "test"
    bind_to_docker_host = True

# TODO handle async
async def _create_integration_step_args(context, results):
    connector_container = results["build"].output_artifact[LOCAL_BUILD_PLATFORM]
    connector_image_tar_file, _ = await export_container_to_tarball(context, connector_container)

    if context.connector.supports_normalization:
        tar_file_name = f"{context.connector.normalization_repository}_{context.git_revision}.tar"
        build_normalization_results = results["build_normalization"]

        normalization_container = build_normalization_results.output_artifact
        normalization_tar_file, _ = await export_container_to_tarball(
            context, normalization_container, tar_file_name=tar_file_name
        )
    else:
        normalization_tar_file = None


    return {
        "connector_tar_file": connector_image_tar_file,
        "normalization_tar_file": normalization_tar_file
    }

def _get_acceptance_test_steps(context: ConnectorContext) -> List[StepToRun]:
    build_steps = [
        StepToRun(
            id="build",
            step=BuildConnectorImages(context, LOCAL_BUILD_PLATFORM),
            args=lambda results: {"dist_dir": results["build_tar"].output_artifact.directory(dist_tar_directory_path(context))},
            depends_on=["build_tar"],
        ),
    ]

    if context.connector.supports_normalization:
        normalization_image = f"{context.connector.normalization_repository}:dev"
        context.logger.info(f"This connector supports normalization: will build {normalization_image}.")
        normalization_steps = [
            StepToRun(
                id="build_normalization",
                step=BuildOrPullNormalization(context, normalization_image, LOCAL_BUILD_PLATFORM),
                depends_on=["build"],
            )
        ]

        build_steps += normalization_steps

    # TODO get this running in parallel
    test_steps = [
        StepToRun(
            id="integration",
            step=IntegrationTests(context),
            args=lambda results: _create_integration_step_args(context, results), ## TODO this wont work as its an async
            depends_on=["build"],
        ),
        StepToRun(
            id="acceptance",
            step=AcceptanceTests(context, True),
            args=lambda results: {"connector_under_test_container": results["build"].output_artifact[LOCAL_BUILD_PLATFORM]},
            depends_on=["build"],
        ),
    ]

    return build_steps + test_steps


def get_test_steps(context: ConnectorContext) -> List[StepToRun]:
    return [
        StepToRun(id="build_tar", step=BuildConnectorDistributionTar(context, LOCAL_BUILD_PLATFORM)),
        # TODO: Ensure unit and acceptance the build steps run in paralell
        StepToRun(id="unit", step=UnitTests(context)),
        _get_acceptance_test_steps(context),
    ]
