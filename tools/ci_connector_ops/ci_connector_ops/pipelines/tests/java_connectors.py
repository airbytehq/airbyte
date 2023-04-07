#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module groups steps made to run tests for a specific Java connector given a test context."""

from typing import List, Optional, Tuple

import anyio
import asyncer
from ci_connector_ops.pipelines.actions import environments, secrets
from ci_connector_ops.pipelines.bases import Step, StepResult, StepStatus
from ci_connector_ops.pipelines.contexts import ConnectorTestContext
from ci_connector_ops.pipelines.tests.common import AcceptanceTests
from ci_connector_ops.pipelines.utils import slugify
from ci_connector_ops.utils import Connector
from dagger import CacheSharingMode, Directory, File, QueryError


class BuildOrPullNormalization(Step):
    """A step to build or pull the normalization image for a connector according to the image name."""

    DESTINATION_SPECIFIC_NORMALIZATION_DOCKERFILE_MAPPING = {
        Connector("destination-clickhouse"): "clickhouse.Dockerfile",
        Connector("destination-duckdb"): "duckdb.Dockerfile",
        Connector("destination-mssql"): "mssql.Dockerfile",
        Connector("destination-mysql"): "mysql.Dockerfile",
        Connector("destination-oracle"): "oracle.Dockerfile",
        Connector("destination-redshift"): "redshift.Dockerfile",
        Connector("destination-snowflake"): "snowflake.Dockerfile",
        Connector("destination-tidb"): "tidb.Dockerfile",
    }

    def __init__(self, context: ConnectorTestContext, normalization_image: str) -> None:
        """Initialize the step to build or pull the normalization image.

        Args:
            context (ConnectorTestContext): The current connector test context.
            normalization_image (str): The normalization image to build (if :dev) or pull.
        """
        super().__init__(context)
        self.use_dev_normalization = normalization_image.endswith(":dev")
        self.normalization_image = normalization_image
        self.normalization_dockerfile = self.DESTINATION_SPECIFIC_NORMALIZATION_DOCKERFILE_MAPPING.get(context.connector, "Dockerfile")
        self.title = f"Build {self.normalization_image}" if self.use_dev_normalization else f"Pull {self.normalization_image}"

    async def _run(self) -> Tuple[StepResult, File]:
        normalization_local_tar_path = f"{slugify(self.normalization_image)}.tar"
        if self.use_dev_normalization:
            normalization_directory = self.context.get_repo_dir("airbyte-integrations/bases/base-normalization")
            sshtunneling_file = self.context.get_repo_dir(
                "airbyte-connector-test-harnesses/acceptance-test-harness/src/main/resources", include="sshtunneling.sh"
            ).file("sshtunneling.sh")
            normalization_directory_with_build = normalization_directory.with_new_directory("build")
            normalization_directory_with_sshtunneling = normalization_directory_with_build.with_file(
                "build/sshtunneling.sh", sshtunneling_file
            )
            build_normalization_container = normalization_directory_with_sshtunneling.docker_build(self.normalization_dockerfile)
        else:
            build_normalization_container = self.context.dagger_client.container().from_(self.normalization_image)
        try:
            export_success = await build_normalization_container.export(f"{self.host_image_export_dir_path}/{normalization_local_tar_path}")
            if export_success:
                exported_file = (
                    self.context.dagger_client.host()
                    .directory(self.host_image_export_dir_path, include=[normalization_local_tar_path])
                    .file(normalization_local_tar_path)
                )
                return StepResult(self, StepStatus.SUCCESS), exported_file
            else:
                return StepResult(self, StepStatus.FAILURE, stderr="The normalization container could not be exported"), None
        except QueryError as e:
            return StepResult(self, StepStatus.FAILURE, stderr=str(e)), None


class GradleTask(Step):
    """
    A step to run a Gradle task.

    Attributes:
        task_name (str): The Gradle task name to run.
        title (str): The step title.
    """

    RUN_AIRBYTE_DOCKER = False

    JAVA_BUILD_INCLUDE = [
        "airbyte-api",
        "airbyte-commons-cli",
        "airbyte-commons-protocol",
        "airbyte-commons",
        "airbyte-config",
        "airbyte-connector-test-harnesses",
        "airbyte-db",
        "airbyte-integrations/bases",
        "airbyte-json-validation",
        "airbyte-protocol",
        "airbyte-test-utils",
    ]

    SOURCE_BUILD_INCLUDE = [
        "airbyte-integrations/connectors/source-jdbc",
        "airbyte-integrations/connectors/source-relational-db",
    ]

    DESTINATION_BUILD_INCLUDE = [
        "airbyte-integrations/connectors/destination-jdbc",
        # destination-bigquery uses utils from destination gcs
        "airbyte-integrations/connectors/destination-gcs",
    ]

    # These are the lines we remove from the connector gradle file to not run acceptance test and not build normalization.
    LINES_TO_REMOVE_FROM_GRADLE_FILE = [
        "id 'airbyte-connector-acceptance-test'",
        "project(':airbyte-integrations:bases:base-normalization').airbyteDocker.output",
    ]

    def __init__(self, context: ConnectorTestContext, gradle_task_name: str, step_title: Optional[str] = None) -> None:
        """Initialize a step to run a Gradle task.

        Args:
            context (ConnectorTestContext): The current connector test context.
            gradle_task_name (str): The name of the gradle task to run.
            step_title (Optional[str], optional): Custom title for the step. Defaults to None.
        """
        super().__init__(context)
        self.task_name = gradle_task_name
        self.title = step_title if step_title else f"Gradle {self.task_name} task"

    @property
    def build_include(self) -> List[str]:
        """Retrieve the list of source code directory required to run a Java connector Gradle task.

        The list is different according to the connector type.

        Returns:
            List[str]: List of directories or files to be mounted to the container to run a Java connector Gradle task.
        """
        if self.context.connector.connector_type == "source":
            return self.JAVA_BUILD_INCLUDE + self.SOURCE_BUILD_INCLUDE
        elif self.context.connector.connector_type == "destination":
            return self.JAVA_BUILD_INCLUDE + self.DESTINATION_BUILD_INCLUDE
        else:
            raise ValueError(f"{self.context.connector.connector_type} is not supported")

    async def _get_patched_connector_dir(self) -> Directory:
        """Patch the build.gradle file of the connector under test.

        - Remove the airbyte-connector-acceptance-test plugin import from build.gradle to not run CAT with Gradle.
        - Do not depend on normalization build to run.
        - Do not run airbyteDocker task if RUN_AIRBYTE_DOCKER is false.

        Returns:
            Directory: The patched connector directory
        """
        if not self.RUN_AIRBYTE_DOCKER:
            lines_to_remove_from_gradle_file = self.LINES_TO_REMOVE_FROM_GRADLE_FILE + ["id 'airbyte-docker'"]
        else:
            lines_to_remove_from_gradle_file = self.LINES_TO_REMOVE_FROM_GRADLE_FILE

        gradle_file_content = await self.context.get_connector_dir(include=["build.gradle"]).file("build.gradle").contents()
        patched_file_content = ""
        for line in gradle_file_content.split("\n"):
            if not any(line_to_remove in line for line_to_remove in lines_to_remove_from_gradle_file):
                patched_file_content += line + "\n"
        return self.context.get_connector_dir(exclude=["build", "secrets"]).with_new_file("build.gradle", patched_file_content)

    def _get_gradle_command(self, extra_options: Tuple[str] = ("--no-daemon", "--scan")) -> List:
        return (
            ["./gradlew"]
            + list(extra_options)
            + [f":airbyte-integrations:connectors:{self.context.connector.technical_name}:{self.task_name}"]
        )

    async def _run(self) -> StepResult:
        connector_java_build_cache = self.context.dagger_client.cache_volume("connector_java_build_cache")

        connector_under_test = (
            environments.with_gradle(self.context, self.build_include)
            .with_mounted_cache(
                f"{self.context.connector.code_directory}/build", connector_java_build_cache, sharing=CacheSharingMode.SHARED
            )
            .with_mounted_directory(str(self.context.connector.code_directory), await self._get_patched_connector_dir())
            # Disable the Ryuk container because it needs privileged docker access that does not work:
            .with_env_variable("TESTCONTAINERS_RYUK_DISABLED", "true")
            .with_directory(f"{self.context.connector.code_directory}/secrets", self.context.secrets_dir)
            .with_exec(self._get_gradle_command())
        )

        return await self.get_step_result(connector_under_test)


class BuildConnectorImage(GradleTask):
    """
    A step to build a Java connector image using the airbyteDocker Gradle task.

    Export the image as a tar archive to host.
    """

    RUN_AIRBYTE_DOCKER = True

    def __init__(self, context: ConnectorTestContext) -> None:
        """Initialize the step to build a connector image with the airbyteDock Gradle task.

        Args:
            context (ConnectorTestContext): The current connector test context.
        """
        super().__init__(context, "airbyteDocker", "Build connector image")

    async def _export_connector_image(self) -> Optional[File]:
        """Save the connector image to the host filesystem as a tar archive.

        Returns:
            Optional[File]: The file object holding the tar archive on the host.
        """
        tar_name = f"{slugify(self.context.connector.technical_name)}.tar"
        image_name = f"airbyte/{self.context.connector.technical_name}:dev"
        export_success = await (
            environments.with_gradle(self.context)
            .with_exec(["docker", "save", "--output", tar_name, image_name])
            .file(tar_name)
            .export(f"{self.host_image_export_dir_path}/{tar_name}")
        )
        if export_success:
            return self.context.dagger_client.host().directory(self.host_image_export_dir_path, include=[tar_name]).file(tar_name)

    async def _run(self) -> Tuple[StepResult, Optional[File]]:
        try:
            connector_java_build_cache = self.context.dagger_client.cache_volume("connector_java_build_cache")
            built_container = (
                environments.with_gradle(self.context, self.build_include)
                .with_mounted_cache(
                    f"{self.context.connector.code_directory}/build", connector_java_build_cache, sharing=CacheSharingMode.SHARED
                )
                .with_mounted_directory(str(self.context.connector.code_directory), await self._get_patched_connector_dir())
                .with_exec(self._get_gradle_command())
            )

            step_result = await self.get_step_result(built_container)
            connector_tar_file = self._export_connector_image()
            return step_result, connector_tar_file
        except QueryError as e:
            return StepResult(self, StepStatus.FAILURE, stderr=str(e)), None


class IntegrationTestJava(GradleTask):
    """A step to run integrations tests for Java connectors using the integrationTestJava Gradle task."""

    def __init__(self, context: ConnectorTestContext) -> None:
        """Initialize the step to run :integrationTestJava Gradle task.

        Args:
            context (ConnectorTestContext): The current connector test context.
        """
        super().__init__(context, "integrationTestJava", step_title="Integration tests")

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
            return StepResult(self, StepStatus.FAILURE, stderr=str(e)), None


async def run_all_tests(context: ConnectorTestContext) -> List[StepResult]:
    """Run all tests for a Java connectors.

    - Build the normalization image if the connector supports it.
    - Run unit tests with Gradle.
    - Build connector image with Gradle.
    - Run integration and acceptance test in parallel using the built connector and normalization images.

    Args:
        context (ConnectorTestContext): The current connector test context.

    Returns:
        List[StepResult]: The results of all the tests steps.
    """
    step_results = []
    unit_test_step = GradleTask(context, "test", step_title="Unit tests")
    build_connector_step = BuildConnectorImage(context)
    build_normalization_step = None
    if context.connector.supports_normalization:
        normalization_image = f"{context.connector.normalization_repository}:dev"
        context.logger.info(f"This connector supports normalization: will build {normalization_image}.")
        build_normalization_step = BuildOrPullNormalization(context, normalization_image)
    integration_test_java_step = IntegrationTestJava(context)
    acceptance_test_step = AcceptanceTests(context)

    context.secrets_dir = await secrets.get_connector_secret_dir(context)

    normalization_tar_file = None
    if build_normalization_step:
        context.logger.info("Run build normalization step.")
        build_normalization_results, normalization_tar_file = await build_normalization_step.run()
        if build_normalization_results.status is StepStatus.FAILURE:
            return step_results + [build_normalization_results, integration_test_java_step.skip(), acceptance_test_step.skip()]
        context.logger.info(f"{build_normalization_step.normalization_image} was successfully built.")
        step_results.append(build_normalization_results)

    context.logger.info("Run unit tests.")
    unit_test_results = await unit_test_step.run()
    if unit_test_results.status is StepStatus.FAILURE:
        return step_results + [unit_test_results, integration_test_java_step.skip(), acceptance_test_step.skip()]
    context.logger.info("Unit tests successfully ran.")
    step_results.append(unit_test_results)

    context.logger.info("Run build connector step")
    build_connector_results, connector_image_tar_file = await build_connector_step.run()
    if build_connector_results.status is StepStatus.FAILURE:
        return step_results + [build_connector_results, integration_test_java_step.skip(), acceptance_test_step.skip()]
    context.logger.info("The connector was successfully built.")
    step_results.append(build_connector_results)

    context.logger.info("Start integration and acceptance tests in parallel.")
    async with asyncer.create_task_group() as task_group:
        tasks = [
            task_group.soonify(integration_test_java_step.run)(connector_image_tar_file, normalization_tar_file),
            task_group.soonify(acceptance_test_step.run)(connector_image_tar_file),
        ]
    return step_results + [task.value for task in tasks]
