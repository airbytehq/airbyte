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


async def run_all_tests(context: ConnectorContext) -> List[StepResult]:
    """Run all tests for a Java connectors.

    - Build the normalization image if the connector supports it.
    - Run unit tests with Gradle.
    - Build connector image with Gradle.
    - Run integration and acceptance test in parallel using the built connector and normalization images.

    Args:
        context (ConnectorContext): The current connector context.

    Returns:
        List[StepResult]: The results of all the tests steps.
    """
    context.connector_secrets = await secrets.get_connector_secrets(context)
    step_results = []

    build_distribution_tar_result = await BuildConnectorDistributionTar(context).run()
    step_results.append(build_distribution_tar_result)
    if build_distribution_tar_result.status is StepStatus.FAILURE:
        return step_results

    dist_tar_dir = build_distribution_tar_result.output_artifact.directory(dist_tar_directory_path(context))

    async def run_docker_build_dependent_steps(dist_tar_dir: Directory) -> List[StepResult]:
        step_results = []
        build_connector_image_results = await BuildConnectorImages(context, LOCAL_BUILD_PLATFORM).run(dist_tar_dir)
        step_results.append(build_connector_image_results)
        if build_connector_image_results.status is StepStatus.FAILURE:
            return step_results

        if context.connector.supports_normalization:
            normalization_image = f"{context.connector.normalization_repository}:dev"
            context.logger.info(f"This connector supports normalization: will build {normalization_image}.")
            build_normalization_results = await BuildOrPullNormalization(context, normalization_image, LOCAL_BUILD_PLATFORM).run()
            normalization_container = build_normalization_results.output_artifact
            normalization_tar_file, _ = await export_container_to_tarball(
                context, normalization_container, tar_file_name=f"{context.connector.normalization_repository}_{context.git_revision}.tar"
            )
            step_results.append(build_normalization_results)
        else:
            normalization_tar_file = None

        connector_container = build_connector_image_results.output_artifact[LOCAL_BUILD_PLATFORM]
        connector_image_tar_file, _ = await export_container_to_tarball(context, connector_container)

        async with asyncer.create_task_group() as docker_build_dependent_group:
            soon_integration_tests_results = docker_build_dependent_group.soonify(IntegrationTests(context).run)(
                connector_tar_file=connector_image_tar_file, normalization_tar_file=normalization_tar_file
            )
            soon_cat_results = docker_build_dependent_group.soonify(AcceptanceTests(context, True).run)(connector_container)

        step_results += [soon_cat_results.value, soon_integration_tests_results.value]
        return step_results

    async with asyncer.create_task_group() as test_task_group:
        soon_unit_tests_result = test_task_group.soonify(UnitTests(context).run)()
        soon_docker_build_dependent_steps_results = test_task_group.soonify(run_docker_build_dependent_steps)(dist_tar_dir)

    return step_results + [soon_unit_tests_result.value] + soon_docker_build_dependent_steps_results.value
