#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from __future__ import annotations

from abc import ABC
from typing import ClassVar, List, Tuple

from dagger import CacheSharingMode, CacheVolume, Container, Directory
from pipelines import consts
from pipelines.actions import environments
from pipelines.bases import Step, StepResult, StepStatus
from pipelines.contexts import PipelineContext
from pipelines.utils import sh_dash_c


class GradleTask(Step, ABC):
    """
    A step to run a Gradle task.

    Attributes:
        task_name (str): The Gradle task name to run.
        title (str): The step title.
    """

    DEFAULT_TASKS_TO_EXCLUDE = ["airbyteDocker"]
    BIND_TO_DOCKER_HOST = True
    DEFAULT_GRADLE_TASK_OPTIONS = ("--no-daemon", "--scan", "--build-cache")
    gradle_task_name: ClassVar
    gradle_task_options: Tuple[str, ...] = ()
    mount_connector_secrets: bool = True

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

    def _get_publish_snapshot_command(self) -> List:
        command = (
            ["./gradlew"]
            + list(self.DEFAULT_GRADLE_TASK_OPTIONS)
            + [":airbyte-cdk:java:airbyte-cdk:publishSnapshotIfNeeded"]
            + list(self.gradle_task_options)
        )
        for task in self.DEFAULT_TASKS_TO_EXCLUDE:
            command += ["-x", task]
        return command

    def _get_gradle_command(self) -> List:
        command = (
                ["./gradlew"]
                + list(self.DEFAULT_GRADLE_TASK_OPTIONS)
                + [f":airbyte-integrations:connectors:{self.context.connector.technical_name}:{self.gradle_task_name}"]
                + list(self.gradle_task_options)
        )
        for task in self.DEFAULT_TASKS_TO_EXCLUDE:
            command += ["-x", task]
        command += ["--debug"]
        gradle = " ".join(command)
        load_from_cache = "rsync -a /root/gradle-cache/ /root/.gradle"
        store_to_cache = "rsync -a /root/.gradle/ /root/gradle-cache"
        with_rsync = f"(set -o xtrace && {load_from_cache} && {gradle} && {store_to_cache}) > /root/stdout.txt 2> /root/stderr.txt"
        return ["sh", "-c", with_rsync]

    async def _run(self) -> StepResult:
        includes = self.build_include + ["airbyte-cdk/java/airbyte-cdk"] if self.with_java_cdk_snapshot else self.build_include

        connector_under_test = (
            self.with_gradle(sources_to_include=includes)
            .with_mounted_directory(str(self.context.connector.code_directory), await self.context.get_connector_dir())
            # Disable the Ryuk container because it needs privileged docker access that does not work:
            .with_env_variable("TESTCONTAINERS_RYUK_DISABLED", "true")
        )
        if self.mount_connector_secrets:
            connector_under_test = connector_under_test.with_(
                environments.mounted_connector_secrets(self.context, f"{self.context.connector.code_directory}/secrets")
            )
        connector_under_test = connector_under_test.with_exec(self._get_gradle_command())

        result = await self.get_step_result(connector_under_test)
        if result.status is StepStatus.SUCCESS:
            await self.export_cache_to_volume(result.output_artifact)
        return result

    async def export_cache_to_volume(self, container):
        await container.with_exec(["rsync", "-az", "/root/.gradle/", "/root/gradle-cache"])

    def with_gradle(
        self,
        sources_to_include: List[str] = None,
    ) -> Container:
        """Create a container with Gradle installed and bound to a persistent docker host.

        Args:
            sources_to_include (List[str], optional): List of additional source path to mount to the container. Defaults to None.
        Returns:
            Container: A container with Gradle installed and Java sources from the repository.
        """

        gradle_cache: CacheVolume = self.dagger_client.cache_volume("gradle-cache")

        include = [
            ".root",
            ".env",
            "build.gradle",
            "deps.toml",
            "gradle.properties",
            "gradle",
            "gradlew",
            "LICENSE_SHORT",
            "publish-repositories.gradle",
            "settings.gradle",
            "build.gradle",
            "tools/gradle",
            "spotbugs-exclude-filter-file.xml",
            "buildSrc",
            "tools/bin/build_image.sh",
            "tools/lib/lib.sh",
            "tools/gradle/codestyle",
            "pyproject.toml",
        ]

        if sources_to_include:
            include += sources_to_include

        openjdk_with_docker = (
            self.dagger_client.container()
            .from_("openjdk:17.0.1-jdk-slim")
            .with_exec(sh_dash_c(
                [
                    "apt-get update",
                    "apt-get install -y curl jq rsync npm pip",
                ]
            ))
            .with_env_variable("VERSION", consts.DOCKER_VERSION)
            .with_exec(["sh", "-c", "curl -fsSL https://get.docker.com | sh"])
            .with_env_variable("GRADLE_HOME", "/root/.gradle")
            .with_env_variable("GRADLE_USER_HOME", "/root/.gradle")
            .with_exec(["mkdir", "/airbyte"])
            .with_workdir("/airbyte")
            .with_env_variable("AIRBYTE_CI", "True")
            .with_mounted_cache("/root/gradle-cache", gradle_cache, sharing=CacheSharingMode.LOCKED)
            .with_exec(["rsync", "-az", "/root/gradle-cache/", "/root/.gradle"])
            .with_mounted_directory("/airbyte", self.context.get_repo_dir(".", include=include))
        )

        if self.BIND_TO_DOCKER_HOST:
            return environments.with_bound_docker_host(self.context, openjdk_with_docker)
        else:
            return openjdk_with_docker
