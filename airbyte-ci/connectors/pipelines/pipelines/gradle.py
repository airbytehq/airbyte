#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from __future__ import annotations

from abc import ABC
from typing import ClassVar, List

from dagger import CacheSharingMode, CacheVolume
from pipelines import hacks
from pipelines.actions import environments
from pipelines.bases import Step, StepResult
from pipelines.consts import AMAZONCORRETTO_IMAGE
from pipelines.contexts import PipelineContext
from pipelines.utils import sh_dash_c


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
    def persistent_cache_volume(self) -> CacheVolume:
        """This cache volume is for sharing gradle state across all pipeline runs."""
        return self.context.dagger_client.cache_volume("gradle-dependency-cache")

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

    def _get_gradle_command(self, task: str, *args) -> str:
        return f"./gradlew {' '.join(self.DEFAULT_GRADLE_TASK_OPTIONS + args)} {task}"

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
        ] + self.build_include

        yum_packages_to_install = [
            "docker",  # required by :integrationTestJava.
            "findutils",  # gradle requires xargs, which is shipped in findutils.
            "jq",  # required by :airbyte-connector-test-harnesses:acceptance-test-harness to inspect docker images.
            "npm",  # required by :format.
            "python3.11-pip",  # required by :format.
            "rsync",  # required for gradle cache synchronization.
        ]

        # Common base container.
        gradle_container_base = (
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
            # Set GRADLE_HOME to the directory which will be rsync-ed with the gradle cache volume.
            .with_env_variable("GRADLE_HOME", "/root/.gradle")
            # Same for GRADLE_USER_HOME.
            .with_env_variable("GRADLE_USER_HOME", "/root/.gradle")
            # Set RUN_IN_AIRBYTE_CI to tell gradle how to configure its build cache.
            # This is consumed by settings.gradle in the repo root.
            .with_env_variable("RUN_IN_AIRBYTE_CI", "1")
            # Disable the Ryuk container because it needs privileged docker access which it can't have.
            .with_env_variable("TESTCONTAINERS_RYUK_DISABLED", "true")
            # Set the current working directory.
            .with_workdir("/airbyte")
        )

        # Mount the whole git repo to update the persistent gradle cache and build the CDK.
        with_whole_git_repo = (
            gradle_container_base
            # Mount the whole repo.
            .with_mounted_directory("/airbyte", self.context.get_repo_dir(".").with_timestamps(1))
            # Mount the cache volume for the gradle cache which is persisted throughout all pipeline runs.
            # We deliberately don't mount any cache volumes before mounting the git repo otherwise these will effectively be always empty.
            # This volume is LOCKED instead of SHARED and we rsync to it instead of mounting it directly to $GRADLE_HOME.
            # This is because gradle doesn't cope well with concurrency.
            .with_mounted_cache("/root/gradle-persistent-cache", self.persistent_cache_volume, sharing=CacheSharingMode.LOCKED)
            # Update the persistent gradle cache by resolving all dependencies.
            # Also, build the java CDK and publish it to the local maven repository.
            .with_exec(
                sh_dash_c(
                    [
                        # Ensure that the local maven repository root directory exists.
                        "mkdir -p /root/.m2",
                        # Load from the persistent cache.
                        "(rsync -a --stats --mkpath /root/gradle-persistent-cache/ /root/.gradle || true)",
                        # Resolve all dependencies and write their checksums to './gradle/verification-metadata.dryrun.xml'.
                        self._get_gradle_command("help", "--write-verification-metadata", "sha256", "--dry-run"),
                        # Build the CDK and publish it to the local maven repository.
                        self._get_gradle_command(":airbyte-cdk:java:airbyte-cdk:publishSnapshotIfNeeded"),
                        # Store to the persistent cache.
                        "(rsync -a --stats /root/.gradle/ /root/gradle-persistent-cache || true)",
                    ]
                )
            )
        )

        # Mount only the code needed to build the connector.
        # This reduces the scope of the inputs to help dagger reuse container layers.
        # The contents of '/root/.gradle' and '/root/.m2' are by design not overly sensitive to changes in the rest of the git repo.
        gradle_container = (
            gradle_container_base
            # TODO: remove this once we finish the project to boost source-postgres CI performance.
            .with_env_variable("CACHEBUSTER", hacks.get_cachebuster(self.context, self.logger))
            # Mount the connector-agnostic whitelisted files in the git repo.
            .with_mounted_directory("/airbyte", self.context.get_repo_dir(".", include=include))
            # Mount the sources for the connector and its dependencies in the git repo.
            .with_mounted_directory(str(self.context.connector.code_directory), await self.context.get_connector_dir())
            # Populate the local maven repository.
            # Awaiting on this other container's directory ensures that the caches have been warmed.
            .with_directory("/root/.m2", await with_whole_git_repo.directory("/root/.m2"))
            # Mount the cache volume for the persistent gradle dependency cache.
            .with_mounted_cache("/root/gradle-persistent-cache", self.persistent_cache_volume, sharing=CacheSharingMode.LOCKED)
            # Warm the gradle cache.
            .with_exec(sh_dash_c(["(rsync -a --stats --mkpath /root/gradle-persistent-cache/ /root/.gradle || true)"]))
        )

        # From this point on, we add layers which are task-dependent.
        secrets_dir = f"{self.context.connector.code_directory}/secrets" if self.mount_connector_secrets else None
        gradle_container = gradle_container.with_(await environments.mounted_connector_secrets(self.context, secrets_dir))
        if self.bind_to_docker_host:
            # If this GradleTask subclass needs docker, then install it and bind it to the existing global docker host container.
            gradle_container = environments.with_bound_docker_host(self.context, gradle_container)
            # This installation should be cheap, as the package has already been downloaded, and its dependencies are already installed.
            gradle_container = gradle_container.with_exec(["yum", "install", "-y", "docker"])

        # Run the gradle task that we actually care about.
        connector_task = f":airbyte-integrations:connectors:{self.context.connector.technical_name}:{self.gradle_task_name}"
        gradle_container = gradle_container.with_exec(sh_dash_c([self._get_gradle_command(connector_task)]))
        return await self.get_step_result(gradle_container)
