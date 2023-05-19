#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from __future__ import annotations

from abc import ABC
from typing import ClassVar, List, Tuple

from ci_connector_ops.pipelines.actions import environments
from ci_connector_ops.pipelines.bases import Step, StepResult
from ci_connector_ops.pipelines.utils import slugify
from ci_connector_ops.utils import Connector
from dagger import CacheVolume, Directory


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
        "airbyte-integrations/bases/bases-destination-jdbc",
        "airbyte-integrations/connectors/destination-gcs",
        "airbyte-integrations/connectors/destination-azure-blob-storage",
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

    def get_related_connectors(self) -> List[Connector]:
        """Retrieve the list of related connectors.
        This is used to include source code of non strict-encrypt connectors when running build for a strict-encrypt connector.

        Returns:
            List[Connector]: The list of related connectors.
        """
        if self.context.connector.technical_name.endswith("-strict-encrypt"):
            return [Connector(self.context.connector.technical_name.replace("-strict-encrypt", ""))]
        if self.context.connector.technical_name == "source-file-secure":
            return [Connector("source-file")]
        if self.context.connector.technical_name == "destination-bigquery-denormalized":
            return [Connector("destination-bigquery")]
        if self.context.connector.technical_name == "destination-dev-null":
            return [Connector("destination-e2e-test")]
        return []

    @property
    def build_include(self) -> List[str]:
        """Retrieve the list of source code directory required to run a Java connector Gradle task.

        The list is different according to the connector type.

        Returns:
            List[str]: List of directories or files to be mounted to the container to run a Java connector Gradle task.
        """
        to_include = self.JAVA_BUILD_INCLUDE

        if self.context.connector.connector_type == "source":
            to_include += self.SOURCE_BUILD_INCLUDE
        elif self.context.connector.connector_type == "destination":
            to_include += self.DESTINATION_BUILD_INCLUDE
        else:
            raise ValueError(f"{self.context.connector.connector_type} is not supported")

        with_related_connectors_source_code = to_include + [str(connector.code_directory) for connector in self.get_related_connectors()]
        return with_related_connectors_source_code

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
