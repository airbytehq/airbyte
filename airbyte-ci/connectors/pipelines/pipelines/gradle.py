#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from __future__ import annotations

from abc import ABC
from typing import Callable, ClassVar, List, Optional, Tuple

from dagger import CacheVolume, Container, Directory, QueryError
from pipelines import consts
from pipelines.actions import environments
from pipelines.bases import Step, StepResult
from pipelines.utils import slugify


class GradleTask(Step, ABC):
    """
    A step to run a Gradle task.

    Attributes:
        task_name (str): The Gradle task name to run.
        title (str): The step title.
    """

    DEFAULT_TASKS_TO_EXCLUDE = ["airbyteDocker"]
    gradle_task_name: ClassVar

    DEFAULT_SOURCES_TO_INCLUDE = [
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

    def _get_gradle_command(self, extra_options: Tuple[str] = ("--no-daemon", "--scan", "--build-cache")) -> List:
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
            self.gradle_container.with_mounted_directory(str(self.context.connector.code_directory), await self.context.get_connector_dir())
            .with_mounted_directory("buildSrc", await self._get_patched_build_src_dir())
            .with_(environments.mounted_connector_secrets(self.context, f"{self.context.connector.code_directory}/secrets"))
            .with_exec(self._get_gradle_command())
        )

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

    @property
    def custom_docker_host_binding(self) -> Optional[Callable]:
        docker_host_name = slugify(f"{self.context.connector.technical_name}-gradle-docker-host")
        return environments.bound_docker_host(self.context, docker_host_name)

    @property
    def gradle_container(
        self,
    ) -> Container:
        """Create a container with Gradle installed and optionally bound to a docker host.

        Returns:
            Container: A container with Gradle installed and Java sources from the repository.
        """

        include = self.DEFAULT_SOURCES_TO_INCLUDE + self.build_include

        # TODO re-enable once we have fixed the over caching issue
        # gradle_dependency_cache: CacheVolume = context.dagger_client.cache_volume("gradle-dependencies-caching")
        # gradle_build_cache: CacheVolume = context.dagger_client.cache_volume(f"{context.connector.technical_name}-gradle-build-cache")

        return (
            self.context.dagger_client.container()
            .from_("openjdk:17.0.1-jdk-slim")
            .with_exec(["apt-get", "update"])
            .with_exec(["apt-get", "install", "-y", "curl", "jq", "rsync", "npm", "pip"])
            .with_env_variable("VERSION", consts.DOCKER_VERSION)
            .with_exec(["sh", "-c", "curl -fsSL https://get.docker.com | sh"])
            .with_env_variable("GRADLE_HOME", "/root/.gradle")
            .with_exec(["mkdir", "/airbyte"])
            .with_workdir("/airbyte")
            .with_mounted_directory("/airbyte", self.context.get_repo_dir(include=include))
            .with_exec(["mkdir", "-p", consts.GRADLE_READ_ONLY_DEPENDENCY_CACHE_PATH])
            # TODO (ben) reenable once we have fixed the over caching issue
            # .with_mounted_cache(consts.GRADLE_BUILD_CACHE_PATH, gradle_build_cache, sharing=CacheSharingMode.LOCKED)
            # .with_mounted_cache(consts.GRADLE_READ_ONLY_DEPENDENCY_CACHE_PATH, gradle_dependency_cache)
            .with_env_variable("GRADLE_RO_DEP_CACHE", consts.GRADLE_READ_ONLY_DEPENDENCY_CACHE_PATH)
            # Disable the Ryuk container because it needs privileged docker access that does not work:
            .with_env_variable("TESTCONTAINERS_RYUK_DISABLED", "true")
            .with_(self.custom_docker_host_binding)
        )
