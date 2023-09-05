#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from __future__ import annotations

from abc import ABC
from typing import ClassVar, List, Tuple

from dagger import CacheVolume, Directory
from pipelines.actions import environments
from pipelines.bases import Step, StepResult, StepStatus
from pipelines.contexts import PipelineContext


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
    gradle_task_options: Tuple[str, ...] = ()

    def __init__(self, context: PipelineContext, with_java_cdk_snapshot: bool = False) -> None:
        super().__init__(context)
        self.with_java_cdk_snapshot = with_java_cdk_snapshot

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
        return [
            str(dependency_directory)
            for dependency_directory in self.context.connector.get_local_dependency_paths(with_test_dependencies=True)
        ]

    async def _get_patched_build_src_dir(self) -> Directory:
        """Patch some gradle plugins.

        Returns:
            Directory: The patched buildSrc directory
        """

        build_src_dir = self.context.get_repo_dir("buildSrc")
        cat_gradle_plugin_content = await build_src_dir.file("src/main/groovy/airbyte-connector-acceptance-test.gradle").contents()
        # When running integrationTest in Dagger we don't want to run connectorAcceptanceTest
        # connectorAcceptanceTest is run in the AcceptanceTest step
        cat_gradle_plugin_content = cat_gradle_plugin_content.replace(
            "project.integrationTest.dependsOn(project.connectorAcceptanceTest)", ""
        )
        return build_src_dir.with_new_file("src/main/groovy/airbyte-connector-acceptance-test.gradle", contents=cat_gradle_plugin_content)

    def _get_gradle_command(
        self,
        extra_options: Tuple[str, ...] = (
            "--scan",
            "--build-cache",
            "--no-daemon",
            "--no-watch-fs",
        ),
    ) -> List:
        command = (
            ["./gradlew"]
            + list(extra_options)
            + [f":airbyte-integrations:connectors:{self.context.connector.technical_name}:{self.gradle_task_name}"]
            + list(self.gradle_task_options)
        )
        for task in self.DEFAULT_TASKS_TO_EXCLUDE:
            command += ["-x", task]
        return command

    async def _run(self) -> StepResult:
        includes = self.build_include
        if self.with_java_cdk_snapshot:
            includes + ["./airbyte-cdk/java/airbyte-cdk/**"]

        connector_under_test = (
            environments.with_gradle(self.context, includes, bind_to_docker_host=self.BIND_TO_DOCKER_HOST)
            .with_mounted_directory(str(self.context.connector.code_directory), await self.context.get_connector_dir())
            .with_mounted_directory("buildSrc", await self._get_patched_build_src_dir())
            # Disable the Ryuk container because it needs privileged docker access that does not work:
            .with_env_variable("TESTCONTAINERS_RYUK_DISABLED", "true")
            .with_(environments.mounted_connector_secrets(self.context, f"{self.context.connector.code_directory}/secrets"))
        )
        if self.with_java_cdk_snapshot:
            connector_under_test = connector_under_test.with_exec(["./gradlew", ":airbyte-cdk:java:airbyte-cdk:publishSnapshotIfNeeded"])
        connector_under_test = connector_under_test.with_exec(self._get_gradle_command())
        result = await self.get_step_result(connector_under_test)
        if result.status is StepStatus.SUCCESS:
            await self.export_cache_to_volume(result.output_artifact)
        return result

    async def export_cache_to_volume(self, container):
        await container.with_exec(["rsync", "-az", "/root/.gradle/", "/root/gradle-cache"])
