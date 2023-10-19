#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC
from typing import ClassVar, List

import pipelines.dagger.actions.system.docker
from dagger import CacheSharingMode, CacheVolume
from pipelines import hacks
from pipelines.consts import AMAZONCORRETTO_IMAGE
from pipelines.dagger.actions import secrets
from pipelines.helpers.utils import sh_dash_c
from pipelines.models.contexts import PipelineContext
from pipelines.models.steps import Step, StepResult


class GradleTask(Step, ABC):
    """
    A step to run a Gradle task.

    Attributes:
        title (str): The step title.
        gradle_task_name (str): The Gradle task name to run.
        bind_to_docker_host (bool): Whether to install the docker client and bind it to the host.
        mount_connector_secrets (bool): Whether to mount connector secrets.
    """

    DEFAULT_GRADLE_TASK_OPTIONS = ("--no-daemon", "--scan", "--build-cache", "--console=plain")

    gradle_task_name: ClassVar[str]
    bind_to_docker_host: ClassVar[bool] = False
    mount_connector_secrets: ClassVar[bool] = False

    def __init__(self, context: PipelineContext) -> None:
        super().__init__(context)

    @property
    def connector_java_build_cache(self) -> CacheVolume:
        # TODO: remove this once we finish the project to boost source-postgres CI performance.
        # We should use a static gradle-cache volume name.
        cache_volume_name = hacks.get_gradle_cache_volume_name(self.context, self.logger)
        return self.context.dagger_client.cache_volume(cache_volume_name)

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

    def _get_gradle_command(self, task: str) -> List[str]:
        return sh_dash_c(
            [
                # The gradle command is chained in between a couple of rsyncs which load from- and store to the cache volume.
                "(rsync -a --stats /root/gradle-cache/ /root/.gradle || true)",
                f"./gradlew {' '.join(self.DEFAULT_GRADLE_TASK_OPTIONS)} {task}",
                "(rsync -a --stats /root/.gradle/ /root/gradle-cache || true)",
            ]
        )

    async def _run(self) -> StepResult:
        include = [
            ".root",
            ".env",
            "build.gradle",
            "deps.toml",
            "gradle.properties",
            "gradle",
            "gradlew",
            "LICENSE_SHORT",
            "settings.gradle",
            "build.gradle",
            "tools/gradle",
            "spotbugs-exclude-filter-file.xml",
            "buildSrc",
            "tools/bin/build_image.sh",
            "tools/lib/lib.sh",
            "tools/gradle/codestyle",
            "pyproject.toml",
            "airbyte-cdk/java/airbyte-cdk/**",
        ] + self.build_include

        yum_packages_to_install = [
            "docker",  # required by :integrationTestJava.
            "findutils",  # gradle requires xargs, which is shipped in findutils.
            "jq",  # required by :airbyte-connector-test-harnesses:acceptance-test-harness to inspect docker images.
            "npm",  # required by :format.
            "python3.11-pip",  # required by :format.
            "rsync",  # required for gradle cache synchronization.
        ]

        # Define a gradle container which will be cached and re-used for all tasks.
        # We should do our best to cram any generic & expensive layers in here.
        gradle_container = (
            self.dagger_client.container()
            # Use a linux+jdk base image with long-term support, such as amazoncorretto.
            .from_(AMAZONCORRETTO_IMAGE)
            # Install a bunch of packages as early as possible.
            .with_exec(
                sh_dash_c(
                    [
                        # Update first, but in the same .with_exec step as the package installation.
                        # Otherwise, we risk caching stale package URLs.
                        "yum update -y",
                        f"yum install -y {' '.join(yum_packages_to_install)}",
                        # Remove any dangly bits.
                        "yum clean all",
                        # Deliberately soft-remove docker, so that the `docker` CLI is unavailable by default.
                        # This is a defensive choice to enforce the expectation that, as a general rule, gradle tasks do not rely on docker.
                        "yum remove -y --noautoremove docker",  # remove docker package but not its dependencies
                        "yum install -y --downloadonly docker",  # have docker package in place for quick install
                    ]
                )
            )
            # Set GRADLE_HOME and GRADLE_USER_HOME to the directory which will be rsync-ed with the gradle cache volume.
            .with_env_variable("GRADLE_HOME", "/root/.gradle")
            .with_env_variable("GRADLE_USER_HOME", "/root/.gradle")
            # Set RUN_IN_AIRBYTE_CI to tell gradle how to configure its build cache.
            # This is consumed by settings.gradle in the repo root.
            .with_env_variable("RUN_IN_AIRBYTE_CI", "1")
            # TODO: remove this once we finish the project to boost source-postgres CI performance.
            .with_env_variable("CACHEBUSTER", hacks.get_cachebuster(self.context, self.logger))
            # Mount the gradle cache volume.
            # We deliberately don't mount it at $GRADLE_HOME, instead we load it there and store it from there using rsync.
            # This is because the volume is accessed concurrently by all GradleTask instances.
            # Hence, why we synchronize the writes by setting the `sharing` parameter to LOCKED.
            .with_mounted_cache("/root/gradle-cache", self.connector_java_build_cache, sharing=CacheSharingMode.LOCKED)
            # Mount the parts of the repo which interest us in /airbyte.
            .with_workdir("/airbyte")
            .with_mounted_directory("/airbyte", self.context.get_repo_dir(".", include=include))
            .with_mounted_directory(str(self.context.connector.code_directory), await self.context.get_connector_dir())
            # Disable the Ryuk container because it needs privileged docker access that does not work:
            .with_env_variable("TESTCONTAINERS_RYUK_DISABLED", "true")
            # Run gradle once to populate the container's local maven repository.
            # This step is useful also to serve as a basic sanity check and to warm the gradle cache.
            # This will download gradle itself, a bunch of poms and jars, compile the gradle plugins, configure tasks, etc.
            .with_exec(self._get_gradle_command(":airbyte-cdk:java:airbyte-cdk:publishSnapshotIfNeeded"))
        )

        # From this point on, we add layers which are task-dependent.
        if self.mount_connector_secrets:
            gradle_container = gradle_container.with_(
                await secrets.mounted_connector_secrets(self.context, f"{self.context.connector.code_directory}/secrets")
            )
        if self.bind_to_docker_host:
            # If this GradleTask subclass needs docker, then install it and bind it to the existing global docker host container.
            gradle_container = pipelines.dagger.actions.system.docker.with_bound_docker_host(self.context, gradle_container)
            # This installation should be cheap, as the package has already been downloaded, and its dependencies are already installed.
            gradle_container = gradle_container.with_exec(["yum", "install", "-y", "docker"])

        # Run the gradle task that we actually care about.
        connector_task = f":airbyte-integrations:connectors:{self.context.connector.technical_name}:{self.gradle_task_name}"
        gradle_container = gradle_container.with_exec(self._get_gradle_command(connector_task))
        return await self.get_step_result(gradle_container)
