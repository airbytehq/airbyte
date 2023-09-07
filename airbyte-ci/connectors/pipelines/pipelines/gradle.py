#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from __future__ import annotations

from abc import ABC
from typing import ClassVar, Tuple

from dagger import CacheVolume, Container, Directory, QueryError
from pipelines import consts
from pipelines.actions import environments
from pipelines.bases import Step, StepResult
from pipelines.contexts import PipelineContext


class GradleTask(Step, ABC):
    """
    A step to run a Gradle task.

    Attributes:
        task_name (str): The Gradle task name to run.
        title (str): The step title.
    """

    DEFAULT_TASKS_TO_EXCLUDE = ["assemble", "airbyteDocker"]
    BIND_TO_DOCKER_HOST = True
    gradle_task_name: ClassVar
    gradle_task_options: Tuple[str, ...] = ()

    def __init__(self, context: PipelineContext, with_java_cdk_snapshot: bool = True) -> None:
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

    def _get_gradle_command(self, extra_options: Tuple[str, ...] = ("--no-daemon", "--scan", "--build-cache")) -> List:
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
            # Disable the Ryuk container because it needs privileged docker access that does not work:
            .with_env_variable("TESTCONTAINERS_RYUK_DISABLED", "true")
            .with_(environments.mounted_connector_secrets(self.context, f"{self.context.connector.code_directory}/secrets"))
        )
        if self.with_java_cdk_snapshot:
            connector_under_test = connector_under_test.with_exec(["./gradlew", ":airbyte-cdk:java:airbyte-cdk:publishSnapshotIfNeeded"])
        connector_under_test = connector_under_test.with_exec(self._get_gradle_command())

        results = await self.get_step_result(connector_under_test)

        await self._export_gradle_dependency_cache(connector_under_test)
        return results

    async def _export_gradle_dependency_cache(self, gradle_container: Container) -> Container:
        """Export the Gradle writable dependency cache to the read-only dependency cache path.
        The read-only dependency cache is persisted thanks to mounted cache volumes in environments.with_gradle().
        You can read more about Shared readonly cache here: https://docs.gradle.org/current/userguide/dependency_resolution.html#sub:shared-readonly-cache
        Args:
            gradle_container (Container): The Gradle container.

        Returns:
            Container: The Gradle container, with the updated cache.
        """
        try:
            cache_dirs = await gradle_container.directory(consts.GRADLE_CACHE_PATH).entries()
        except QueryError:
            cache_dirs = []
        if "modules-2" in cache_dirs:
            with_cache = gradle_container.with_exec(
                [
                    "rsync",
                    "--archive",
                    "--quiet",
                    "--times",
                    "--exclude",
                    "*.lock",
                    "--exclude",
                    "gc.properties",
                    f"{consts.GRADLE_CACHE_PATH}/modules-2/",
                    f"{consts.GRADLE_READ_ONLY_DEPENDENCY_CACHE_PATH}/modules-2/",
                ]
            )
            return await with_cache
        return gradle_container
