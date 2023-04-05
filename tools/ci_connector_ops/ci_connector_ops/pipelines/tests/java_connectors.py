#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module groups steps made to run tests for a specific Java connector given a test context."""

from typing import List, Optional, Tuple

import asyncer
from ci_connector_ops.pipelines.actions import environments, secrets
from ci_connector_ops.pipelines.bases import Step, StepResult, StepStatus
from ci_connector_ops.pipelines.contexts import ConnectorTestContext
from ci_connector_ops.pipelines.tests.common import AcceptanceTests
from ci_connector_ops.utils import Connector
from dagger import CacheSharingMode, Directory, File, QueryError

DOCKER_CACHE_VOLUME_NAME = "docker-lib-java-connectors"

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


def get_normalization_dockerfile(connector: Connector) -> Optional[str]:
    if connector.supports_normalization:
        return DESTINATION_SPECIFIC_NORMALIZATION_DOCKERFILE_MAPPING.get(connector, "Dockerfile")


def get_normalization_image_name(connector: Connector) -> Optional[str]:
    return f"{connector.normalization_repository}:dev"


async def build_and_export_normalization_image(
    context: ConnectorTestContext, normalization_dockerfile: str, normalization_image_name: str
) -> Optional[File]:
    normalization_directory = context.get_repo_dir("airbyte-integrations/bases/base-normalization")

    normalization_local_tar_path = f"{normalization_image_name.replace(':dev', '').replace('/', '_')}.tar"
    build_normalization_container = normalization_directory.docker_build(normalization_dockerfile)
    export_success = await build_normalization_container.export(f"/tmp/{normalization_local_tar_path}")
    if export_success:
        exported_file = (
            context.dagger_client.host().directory("/tmp", include=[normalization_local_tar_path]).file(normalization_local_tar_path)
        )
        return exported_file


class GradleTask(Step):
    @property
    def title(self) -> str:
        return f"Gradle {self.task_name} task"

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
        # destination-bigquery uses utils from destination gcs
        "airbyte-integrations/connectors/destination-gcs",
    ]

    # These are the lines we remove from the connector gradle file to not run acceptance test and not build normalization.
    LINES_TO_REMOVE_FROM_GRADLE_FILE = [
        "id 'airbyte-connector-acceptance-test'",
        "project(':airbyte-integrations:bases:base-normalization').airbyteDocker.output",
    ]

    def __init__(self, context: ConnectorTestContext, gradle_task_name: str) -> None:
        super().__init__(context)
        self.task_name = gradle_task_name

    @property
    def build_include(self) -> List[str]:
        if self.context.connector.connector_type == "source":
            return self.JAVA_BUILD_INCLUDE + self.SOURCE_BUILD_INCLUDE
        else:
            return self.JAVA_BUILD_INCLUDE + self.DESTINATION_BUILD_INCLUDE

    async def get_patched_connector_dir(self) -> Directory:
        """Patch the build.gradle file of the connector under test:
        - Removes the airbyte-connector-acceptance-test plugin import from build.gradle to not run CAT with Gradle.
        - Do not depend on normalization build to run
        Returns:
            Directory: The patched connector directory
        """
        gradle_file_content = await self.context.get_connector_dir(include=["build.gradle"]).file("build.gradle").contents()
        patched_file_content = ""
        for line in gradle_file_content.split("\n"):
            if not any(line_to_remove in line for line_to_remove in self.LINES_TO_REMOVE_FROM_GRADLE_FILE):
                patched_file_content += line + "\n"
        return self.context.get_connector_dir(exclude=["build", "secrets"]).with_new_file("build.gradle", patched_file_content)

    def get_gradle_command(self, extra_options: Tuple[str] = ("--no-daemon",)) -> List:
        return (
            ["./gradlew"]
            + list(extra_options)
            + [f":airbyte-integrations:connectors:{self.context.connector.technical_name}:{self.task_name}"]
        )

    async def _run(self) -> StepResult:
        self.context.dagger_client = self.get_dagger_pipeline(self.context.dagger_client)
        connector_java_build_cache = self.context.dagger_client.cache_volume("connector_java_build_cache")

        connector_under_test = (
            environments.with_gradle(self.context, self.build_include, docker_cache_volume_name=DOCKER_CACHE_VOLUME_NAME)
            .with_mounted_cache(
                f"{self.context.connector.code_directory}/build", connector_java_build_cache, sharing=CacheSharingMode.SHARED
            )
            .with_mounted_directory(str(self.context.connector.code_directory), await self.get_patched_connector_dir())
            # Disable the Ryuk container because it needs privileged docker access that does not work:
            .with_env_variable("TESTCONTAINERS_RYUK_DISABLED", "true")
            .with_directory(f"{self.context.connector.code_directory}/secrets", self.context.secrets_dir)
            .with_exec(self.get_gradle_command())
        )

        return await self.get_step_result(connector_under_test)


class IntegrationTestJava(GradleTask):
    def __init__(self, context: ConnectorTestContext) -> None:
        super().__init__(context, "integrationTestJava")

    async def load_normalization_image(self, normalization_tar_file: File):
        docker_cli = environments.with_docker_cli(self.context, docker_cache_volume_name=DOCKER_CACHE_VOLUME_NAME).with_mounted_file(
            "normalization.tar", normalization_tar_file
        )
        image_load_output = await docker_cli.with_exec(["docker", "load", "--input", "normalization.tar"]).stdout()
        normalization_image_tag = f"{self.context.connector.normalization_repository}:dev"
        image_id = image_load_output.replace("\n", "").replace("Loaded image ID: sha256:", "")
        await docker_cli.with_exec(["docker", "tag", image_id, normalization_image_tag]).exit_code()

    async def _export_connector_image(self) -> Optional[File]:
        tar_name = f"airbyte_{self.context.connector.technical_name}_dev.tar"
        image_name = f"airbyte/{self.context.connector.technical_name}:dev"
        export_success = await (
            environments.with_gradle(self.context, docker_cache_volume_name=DOCKER_CACHE_VOLUME_NAME)
            .with_exec(["docker", "save", "--output", tar_name, image_name])
            .file(tar_name)
            .export(f"/tmp/{tar_name}")
        )
        if export_success:
            return self.context.dagger_client.host().directory("/tmp", include=[tar_name]).file(tar_name)

    async def _run(self, normalization_tar_file: Optional[File]) -> StepResult:
        try:
            if normalization_tar_file:
                await self.load_normalization_image(normalization_tar_file)
            return await super()._run()
        except QueryError as e:
            return StepResult(self, StepStatus.FAILURE, stderr=str(e)), None


class BuildConnectorImage(GradleTask):
    def __init__(self, context: ConnectorTestContext) -> None:
        super().__init__(context, "airbyteDocker")

    async def _export_connector_image(self) -> Optional[File]:
        tar_name = f"airbyte_{self.context.connector.technical_name}_dev.tar"
        image_name = f"airbyte/{self.context.connector.technical_name}:dev"
        export_success = await (
            environments.with_gradle(self.context, docker_cache_volume_name=DOCKER_CACHE_VOLUME_NAME)
            .with_exec(["docker", "save", "--output", tar_name, image_name])
            .file(tar_name)
            .export(f"/tmp/{tar_name}")
        )
        if export_success:
            return self.context.dagger_client.host().directory("/tmp", include=[tar_name]).file(tar_name)

    async def _run(self) -> Tuple[StepResult, Optional[File]]:
        connector_tar_file = None

        self.context.dagger_client = self.get_dagger_pipeline(self.context.dagger_client)
        connector_java_build_cache = self.context.dagger_client.cache_volume("connector_java_build_cache")
        built_container = (
            environments.with_gradle(self.context, self.build_include, docker_cache_volume_name=DOCKER_CACHE_VOLUME_NAME)
            .with_mounted_cache(
                f"{self.context.connector.code_directory}/build", connector_java_build_cache, sharing=CacheSharingMode.SHARED
            )
            .with_mounted_directory(str(self.context.connector.code_directory), await self.get_patched_connector_dir())
            .with_exec(self.get_gradle_command())
        )

        step_result = await self.get_step_result(built_container)

        tar_name = f"airbyte_{self.context.connector.technical_name}_dev.tar"
        image_name = f"airbyte/{self.context.connector.technical_name}:dev"
        export_success = await (
            built_container.with_exec(["docker", "save", "--output", tar_name, image_name]).file(tar_name).export(f"/tmp/{tar_name}")
        )
        if export_success:
            connector_tar_file = self.context.dagger_client.host().directory("/tmp", include=[tar_name]).file(tar_name)
        return step_result, connector_tar_file


async def run_all_tests(context: ConnectorTestContext) -> List[StepResult]:
    step_results = []
    test_step = GradleTask(context, "test")
    build_connector_step = BuildConnectorImage(context)
    integration_test_java_step = IntegrationTestJava(context)
    acceptance_test_step = AcceptanceTests(context)

    context.secrets_dir = await secrets.get_connector_secret_dir(context)
    test_results = await test_step.run()
    if test_results.status is StepStatus.FAILURE:
        return step_results + [test_results, integration_test_java_step.skip(), acceptance_test_step.skip()]
    step_results.append(test_results)

    normalization_tar_file = None
    if context.connector.supports_normalization:
        normalization_dockerfile = get_normalization_dockerfile(context.connector)
        normalization_image_name = get_normalization_image_name(context.connector)
        normalization_tar_file = await build_and_export_normalization_image(context, normalization_dockerfile, normalization_image_name)

    connector_image_tar_file = None
    if context.connector.acceptance_test_config is not None:
        build_connector_results, connector_image_tar_file = await build_connector_step.run()
        if build_connector_results.status is StepStatus.FAILURE:
            return step_results + [integration_test_java_step.skip(), acceptance_test_step.skip()]
        step_results.append(build_connector_results)

    async with asyncer.create_task_group() as task_group:
        tasks = [
            task_group.soonify(integration_test_java_step.run)(normalization_tar_file),
            task_group.soonify(acceptance_test_step.run)(connector_image_tar_file),
        ]
    return step_results + [task.value for task in tasks]
