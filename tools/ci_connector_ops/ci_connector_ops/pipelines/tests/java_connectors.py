#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module groups steps made to run tests for a specific Java connector given a test context."""

from abc import ABC
from typing import ClassVar, List, Optional, Tuple

import anyio
from ci_connector_ops.pipelines.actions import environments, secrets
from ci_connector_ops.pipelines.bases import Step, StepResult, StepStatus
from ci_connector_ops.pipelines.contexts import ConnectorTestContext
from ci_connector_ops.pipelines.tests.common import AcceptanceTests
from ci_connector_ops.pipelines.utils import slugify
from ci_connector_ops.utils import Connector
from dagger import CacheVolume, Container, Directory, File, QueryError


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
            build_normalization_container = environments.with_normalization(self.context, self.normalization_dockerfile)
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


class GradleTask(Step, ABC):
    """
    A step to run a Gradle task.

    Attributes:
        task_name (str): The Gradle task name to run.
        title (str): The step title.
    """

    DEFAULT_TASKS_TO_EXCLUDE = ["airbyteDocker"]
    BIND_TO_DOCKER_HOST = True
    gradle_task_name: ClassVar

    # TODO more robust way to find all projects on which the task depends?
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
        "airbyte-config-oss",
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

    # These are the lines we remove from the connector gradle file to ignore specific tasks / plugins.
    LINES_TO_REMOVE_FROM_GRADLE_FILE = [
        # Do not build normalization with Gradle - we build normalization with Dagger in the BuildOrPullNormalization step.
        "project(':airbyte-integrations:bases:base-normalization').airbyteDocker.output",
    ]

    @property
    def docker_service_name(self) -> str:
        return slugify(f"gradle-{self.title}")

    @property
    def connector_java_build_cache(self) -> CacheVolume:
        return self.context.dagger_client.cache_volume("connector_java_build_cache")

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
        """Patch the build.gradle file of the connector under test by removing the lines declared in LINES_TO_REMOVE_FROM_GRADLE_FILE.

        Returns:
            Directory: The patched connector directory
        """

        gradle_file_content = await self.context.get_connector_dir(include=["build.gradle"]).file("build.gradle").contents()
        patched_file_content = ""
        for line in gradle_file_content.split("\n"):
            if not any(line_to_remove in line for line_to_remove in self.LINES_TO_REMOVE_FROM_GRADLE_FILE):
                patched_file_content += line + "\n"
        return self.context.get_connector_dir().with_new_file("build.gradle", patched_file_content)

    def _get_gradle_command(self, extra_options: Tuple[str] = ("--no-daemon", "--scan")) -> List:
        command = (
            ["./gradlew"]
            + list(extra_options)
            + [f":airbyte-integrations:connectors:{self.context.connector.technical_name}:{self.gradle_task_name}"]
        )
        for task in self.DEFAULT_TASKS_TO_EXCLUDE:
            command += ["-x", task]
        return command

    async def _run(self) -> StepResult:

        connector_under_test = (
            environments.with_gradle(
                self.context, self.build_include, docker_service_name=self.docker_service_name, bind_to_docker_host=self.BIND_TO_DOCKER_HOST
            )
            .with_mounted_directory(str(self.context.connector.code_directory), await self._get_patched_connector_dir())
            # Disable the Ryuk container because it needs privileged docker access that does not work:
            .with_env_variable("TESTCONTAINERS_RYUK_DISABLED", "true")
            .with_directory(f"{self.context.connector.code_directory}/secrets", self.context.secrets_dir)
            .with_exec(self._get_gradle_command())
        )

        return await self.get_step_result(connector_under_test)


class UnitTests(GradleTask):
    title = "Unit tests"
    gradle_task_name = "test"


class BuildConnectorImage(GradleTask):
    """
    A step to build a Java connector image using the build Gradle task.

    Export the image as a tar archive to host.
    """

    title = "Build Connector Image"
    gradle_task_name = "distTar"

    async def _export_connector_image(self, connector: Container) -> Optional[File]:
        """Save the connector image to the host filesystem as a tar archive.

        Returns:
            Optional[File]: The file object holding the tar archive on the host.
        """
        connector_image_tar = f"{self.context.connector.technical_name}.tar"
        export_success = await connector.export(f"{self.host_image_export_dir_path}/{connector_image_tar}")
        if export_success:
            exported_file = (
                self.context.dagger_client.host()
                .directory(self.host_image_export_dir_path, include=[connector_image_tar])
                .file(connector_image_tar)
            )
            return exported_file
        else:
            return None

    async def build_tar(self) -> File:
        distTar = (
            environments.with_gradle(
                self.context,
                self.build_include,
                docker_service_name=self.docker_service_name,
                bind_to_docker_host=self.BIND_TO_DOCKER_HOST,
            )
            .with_mounted_directory(str(self.context.connector.code_directory), await self._get_patched_connector_dir())
            .with_exec(self._get_gradle_command())
            .with_workdir(f"{self.context.connector.code_directory}/build/distributions")
        )

        distributions = await distTar.directory(".").entries()
        tar_files = [f for f in distributions if f.endswith(".tar")]
        if len(tar_files) > 1:
            raise Exception(
                "The distributions directory contains multiple connector tar files. We can't infer which one should be used for the text. Please review and delete any unnecessary tar files."
            )
        return distTar.file(tar_files[0])

    async def _run(self) -> Tuple[StepResult, Optional[File]]:
        try:
            tar_file = await self.build_tar()
            java_connector = await environments.with_airbyte_java_connector(self.context, tar_file)
            step_result = await self.get_step_result(java_connector)
            connector_image_tar_file = await self._export_connector_image(java_connector)

            if connector_image_tar_file is None:
                step_result = StepResult(self, StepStatus.FAILURE, stderr="The java connector could not be exported to the host FS.")
            return step_result, connector_image_tar_file
        except QueryError as e:
            return StepResult(self, StepStatus.FAILURE, stderr=str(e)), None


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
    build_connector_step = BuildConnectorImage(context)
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
        build_normalization_results, normalization_tar_file = await build_normalization_step.run()
        if build_normalization_results.status is StepStatus.FAILURE:
            return step_results + [
                build_normalization_results,
                build_connector_step.skip(),
                unit_tests_step.skip(),
                integration_tests_java_step.skip(),
                acceptance_tests_step.skip(),
            ]
        context.logger.info(f"{build_normalization_step.normalization_image} was successfully built.")
        step_results.append(build_normalization_results)

    context.logger.info("Run build connector step")
    build_connector_results, connector_image_tar_file = await build_connector_step.run()
    if build_connector_results.status is StepStatus.FAILURE:
        return step_results + [
            build_connector_results,
            unit_tests_step.skip(),
            integration_tests_java_step.skip(),
            acceptance_tests_step.skip(),
        ]
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
