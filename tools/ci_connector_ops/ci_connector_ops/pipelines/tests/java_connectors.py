#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module groups steps made to run tests for a specific Java connector given a test context."""

from typing import List, Optional

import anyio
from ci_connector_ops.pipelines.actions import environments, secrets
from ci_connector_ops.pipelines.bases import GradleTask, StepResult, StepStatus
from ci_connector_ops.pipelines.builds import LOCAL_BUILD_PLATFORM
from ci_connector_ops.pipelines.builds.java_connectors import BuildConnectorImage
from ci_connector_ops.pipelines.builds.normalization import BuildOrPullNormalization
from ci_connector_ops.pipelines.contexts import ConnectorContext
from ci_connector_ops.pipelines.tests.common import AcceptanceTests
from ci_connector_ops.pipelines.utils import export_container_to_tarball
from dagger import File, QueryError


class UnitTests(GradleTask):
    title = "Unit tests"
    gradle_task_name = "test"


class IntegrationTestJava(GradleTask):
    """A step to run integrations tests for Java connectors using the integrationTestJava Gradle task."""

    title = "Integration tests"
    gradle_task_name = "integrationTestJava"

    async def _load_normalization_image(self, normalization_tar_file: File):
        normalization_image_tag = f"{self.context.connector.normalization_repository}:dev"
        self.context.logger.info("Load the normalization image to the docker host.")
        await environments.load_image_to_docker_host(
            self.context, normalization_tar_file, normalization_image_tag, docker_service_name=self.docker_service_name
        )
        self.context.logger.info("Successfully loaded the normalization image to the docker host.")

    async def _load_connector_image(self, connector_tar_file: File):
        connector_image_tag = f"airbyte/{self.context.connector.technical_name}:dev"
        self.context.logger.info("Load the connector image to the docker host")
        await environments.load_image_to_docker_host(
            self.context, connector_tar_file, connector_image_tag, docker_service_name=self.docker_service_name
        )
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
    step_results = []
    build_connector_step = BuildConnectorImage(context, LOCAL_BUILD_PLATFORM)
    unit_tests_step = UnitTests(context)
    build_normalization_step = None
    if context.connector.supports_normalization:
        normalization_image = f"{context.connector.normalization_repository}:dev"
        context.logger.info(f"This connector supports normalization: will build {normalization_image}.")
        build_normalization_step = BuildOrPullNormalization(context, normalization_image)
    integration_tests_java_step = IntegrationTestJava(context)
    acceptance_tests_step = AcceptanceTests(context)

    normalization_tar_file = None
    if build_normalization_step:
        context.logger.info("Run build normalization step.")
        build_normalization_results, normalization_container = await build_normalization_step.run()
        if build_normalization_results.status is StepStatus.FAILURE:
            return step_results + [
                build_normalization_results,
                build_connector_step.skip(),
                unit_tests_step.skip(),
                integration_tests_java_step.skip(),
                acceptance_tests_step.skip(),
            ]
        normalization_tar_file, _ = await export_container_to_tarball(context, normalization_container)
        context.logger.info(f"{build_normalization_step.normalization_image} was successfully built.")
        step_results.append(build_normalization_results)

    context.logger.info("Run build connector step")
    build_connector_results, connector_container = await build_connector_step.run()
    if build_connector_results.status is StepStatus.FAILURE:
        return step_results + [
            build_connector_results,
            unit_tests_step.skip(),
            integration_tests_java_step.skip(),
            acceptance_tests_step.skip(),
        ]
    connector_image_tar_file, _ = await export_container_to_tarball(context, connector_container)
    context.logger.info("The connector was successfully built.")
    step_results.append(build_connector_results)

    context.secrets_dir = await secrets.get_connector_secret_dir(context)

    context.logger.info("Run unit tests.")
    unit_test_results = await unit_tests_step.run()
    if unit_test_results.status is StepStatus.FAILURE:
        return step_results + [
            unit_test_results,
            build_connector_step.skip(),
            integration_tests_java_step.skip(),
            acceptance_tests_step.skip(),
        ]
    context.logger.info("Unit tests successfully ran.")
    step_results.append(unit_test_results)

    context.logger.info("Start acceptance tests.")
    acceptance_test_results = await acceptance_tests_step.run(connector_image_tar_file)
    step_results.append(acceptance_test_results)
    context.logger.info("Start integration tests.")
    integration_test_results = await integration_tests_java_step.run(connector_image_tar_file, normalization_tar_file)
    step_results.append(integration_test_results)
    return step_results
