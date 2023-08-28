#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module groups steps made to run tests for a specific Java connector given a test context."""

from typing import List, Optional

import anyio
from dagger import File, QueryError
from pipelines.actions import environments, secrets
from pipelines.bases import StepResult, StepStatus
from pipelines.builds import LOCAL_BUILD_PLATFORM
from pipelines.builds.java_connectors import BuildConnectorDistributionTar, BuildConnectorImage
from pipelines.builds.normalization import BuildOrPullNormalization
from pipelines.contexts import ConnectorContext
from pipelines.gradle import GradleTask
from pipelines.tests.common import AcceptanceTests
from pipelines.utils import export_container_to_tarball


class IntegrationTests(GradleTask):
    """A step to run integrations tests for Java connectors using the integrationTestJava Gradle task."""

    gradle_task_name = "integrationTest"
    DEFAULT_TASKS_TO_EXCLUDE = ["airbyteDocker"]
    title = "Java Connector Integration Tests"

    async def _load_normalization_image(self, normalization_tar_file: File):
        normalization_image_tag = f"{self.context.connector.normalization_repository}:dev"
        self.context.logger.info("Load the normalization image to the docker host.")
        await environments.load_image_to_docker_host(self.context, normalization_tar_file, normalization_image_tag)
        self.context.logger.info("Successfully loaded the normalization image to the docker host.")

    async def _load_connector_image(self, connector_tar_file: File):
        connector_image_tag = f"airbyte/{self.context.connector.technical_name}:dev"
        self.context.logger.info("Load the connector image to the docker host")
        await environments.load_image_to_docker_host(self.context, connector_tar_file, connector_image_tag)
        self.context.logger.info("Successfully loaded the connector image to the docker host.")

    async def _run(self, connector_tar_file: File, normalization_tar_file: Optional[File]) -> StepResult:
        try:
            async with anyio.create_task_group() as tg:
                if normalization_tar_file:
                    tg.start_soon(self._load_normalization_image, normalization_tar_file)
                tg.start_soon(self._load_connector_image, connector_tar_file)
            return await super()._run()
        except QueryError as e:
            return StepResult(self, StepStatus.FAILURE, stderr=str(e))


class UnitTests(GradleTask):
    """A step to run unit tests for Java connectors."""

    title = "Java Connector Unit Tests"
    gradle_task_name = "test"
    context: ConnectorContext

    @property
    def gradle_task_options(self) -> tuple[str, ...]:
        """Return the Gradle task options to use when running unit tests."""
        if self.context.fail_fast:
            return ("--fail-fast",)

        return ()


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

    unit_tests_results = await UnitTests(context).run()
    step_results.append(unit_tests_results)

    if context.fail_fast and unit_tests_results.status is StepStatus.FAILURE:
        return step_results

    build_distribution_tar_results = await BuildConnectorDistributionTar(context).run()
    step_results.append(build_distribution_tar_results)
    if build_distribution_tar_results.status is StepStatus.FAILURE:
        return step_results

    build_connector_image_results = await BuildConnectorImage(context, LOCAL_BUILD_PLATFORM).run(
        build_distribution_tar_results.output_artifact
    )
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

    connector_image_tar_file, _ = await export_container_to_tarball(context, build_connector_image_results.output_artifact)

    integration_tests_results = await IntegrationTests(context).run(connector_image_tar_file, normalization_tar_file)
    step_results.append(integration_tests_results)

    acceptance_tests_results = await AcceptanceTests(context).run(connector_image_tar_file)
    step_results.append(acceptance_tests_results)
    return step_results
