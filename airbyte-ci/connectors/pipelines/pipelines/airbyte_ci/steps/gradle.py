#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC
from typing import ClassVar, List

import pipelines.dagger.actions.system.docker
from dagger import CacheSharingMode, CacheVolume
from pipelines.consts import AMAZONCORRETTO_IMAGE
from pipelines.dagger.actions import secrets
from pipelines.helpers.utils import sh_dash_c
from pipelines.models.contexts.pipeline_context import PipelineContext
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

    DEFAULT_GRADLE_TASK_OPTIONS = ("--no-daemon", "--no-watch-fs", "--scan", "--build-cache", "--console=plain")
    LOCAL_MAVEN_REPOSITORY_PATH = "/root/.m2"
    GRADLE_DEP_CACHE_PATH = "/root/gradle-cache"
    GRADLE_HOME_PATH = "/root/.gradle"

    gradle_task_name: ClassVar[str]
    bind_to_docker_host: ClassVar[bool] = False
    mount_connector_secrets: ClassVar[bool] = False

    def __init__(self, context: PipelineContext) -> None:
        super().__init__(context)

    @property
    def dependency_cache_volume(self) -> CacheVolume:
        """This cache volume is for sharing gradle dependencies (jars and poms) across all pipeline runs."""
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
            "settings.gradle",
            "build.gradle",
            "tools/gradle",
            "spotbugs-exclude-filter-file.xml",
            "buildSrc",
            "tools/bin/build_image.sh",
            "tools/lib/lib.sh",
            "pyproject.toml",
        ] + self.build_include

        yum_packages_to_install = [
            "docker",  # required by :integrationTestJava.
            "findutils",  # gradle requires xargs, which is shipped in findutils.
            "jq",  # required by :acceptance-test-harness to inspect docker images.
            "rsync",  # required for gradle cache synchronization.
        ]

        # Common base container.
        gradle_container_base = (
            self.dagger_client.container()
            # Use a linux+jdk base image with long-term support, such as amazoncorretto.
            .from_(AMAZONCORRETTO_IMAGE)
            # Mount the dependency cache volume, but not to $GRADLE_HOME, because gradle doesn't expect concurrent modifications.
            .with_mounted_cache(self.GRADLE_DEP_CACHE_PATH, self.dependency_cache_volume, sharing=CacheSharingMode.LOCKED)
            # Set GRADLE_HOME to the directory which will be rsync-ed with the gradle cache volume.
            .with_env_variable("GRADLE_HOME", self.GRADLE_HOME_PATH)
            # Same for GRADLE_USER_HOME.
            .with_env_variable("GRADLE_USER_HOME", self.GRADLE_HOME_PATH)
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
            # Set RUN_IN_AIRBYTE_CI to tell gradle how to configure its build cache.
            # This is consumed by settings.gradle in the repo root.
            .with_env_variable("RUN_IN_AIRBYTE_CI", "1")
            # Disable the Ryuk container because it needs privileged docker access which it can't have.
            .with_env_variable("TESTCONTAINERS_RYUK_DISABLED", "true")
            # Set the current working directory.
            .with_workdir("/airbyte")
        )

        # Augment the base container with S3 build cache secrets when available.
        if self.context.s3_build_cache_access_key_id:
            gradle_container_base = gradle_container_base.with_secret_variable(
                "S3_BUILD_CACHE_ACCESS_KEY_ID", self.context.s3_build_cache_access_key_id_secret
            )
            if self.context.s3_build_cache_secret_key:
                gradle_container_base = gradle_container_base.with_secret_variable(
                    "S3_BUILD_CACHE_SECRET_KEY", self.context.s3_build_cache_secret_key_secret
                )

        # Running a gradle task like "help" with these arguments will trigger updating all dependencies.
        # When the cache is cold, this downloads many gigabytes of jars and poms from all over the internet.
        warm_dependency_cache_args = ["--write-verification-metadata", "sha256", "--dry-run"]
        if self.context.is_local:
            # When running locally, this dependency update is slower and less useful than within a CI runner. Skip it.
            warm_dependency_cache_args = ["--dry-run"]

        # Mount the whole git repo to update the cache volume contents and build the CDK.
        with_whole_git_repo = (
            gradle_container_base
            # Mount the whole repo.
            .with_directory("/airbyte", self.context.get_repo_dir("."))
            # Update the cache in place by executing a gradle task which will update all dependencies and build the CDK.
            .with_exec(
                sh_dash_c(
                    [
                        # Ensure that the .m2 directory exists.
                        f"mkdir -p {self.LOCAL_MAVEN_REPOSITORY_PATH}",
                        # Load from the cache volume.
                        f"(rsync -a --stats --mkpath {self.GRADLE_DEP_CACHE_PATH}/ {self.GRADLE_HOME_PATH} || true)",
                        # Resolve all dependencies and write their checksums to './gradle/verification-metadata.dryrun.xml'.
                        self._get_gradle_command("help", *warm_dependency_cache_args),
                        # Build the CDK and publish it to the local maven repository.
                        self._get_gradle_command(":airbyte-cdk:java:airbyte-cdk:publishSnapshotIfNeeded"),
                        # Store to the cache volume.
                        f"(rsync -a --stats {self.GRADLE_HOME_PATH}/ {self.GRADLE_DEP_CACHE_PATH} || true)",
                    ]
                )
            )
        )

        # Mount only the code needed to build the connector.
        gradle_container = (
            gradle_container_base
            # Copy the local maven repository and force evaluation of `with_whole_git_repo` container.
            .with_directory(self.LOCAL_MAVEN_REPOSITORY_PATH, await with_whole_git_repo.directory(self.LOCAL_MAVEN_REPOSITORY_PATH))
            # Mount the connector-agnostic whitelisted files in the git repo.
            .with_mounted_directory("/airbyte", self.context.get_repo_dir(".", include=include))
            # Mount the sources for the connector and its dependencies in the git repo.
            .with_mounted_directory(str(self.context.connector.code_directory), await self.context.get_connector_dir())
        )

        # From this point on, we add layers which are task-dependent.
        if self.mount_connector_secrets:
            secrets_dir = f"{self.context.connector.code_directory}/secrets"
            gradle_container = gradle_container.with_(await secrets.mounted_connector_secrets(self.context, secrets_dir))
        if self.bind_to_docker_host:
            # If this GradleTask subclass needs docker, then install it and bind it to the existing global docker host container.
            gradle_container = pipelines.dagger.actions.system.docker.with_bound_docker_host(self.context, gradle_container)
            # This installation should be cheap, as the package has already been downloaded, and its dependencies are already installed.
            gradle_container = gradle_container.with_exec(["yum", "install", "-y", "docker"])

        # Run the gradle task that we actually care about.
        connector_task = f":airbyte-integrations:connectors:{self.context.connector.technical_name}:{self.gradle_task_name}"
        gradle_container = gradle_container.with_exec(
            sh_dash_c(
                [
                    # Warm the gradle cache.
                    f"(rsync -a --stats --mkpath {self.GRADLE_DEP_CACHE_PATH}/ {self.GRADLE_HOME_PATH} || true)",
                    # Run the gradle task.
                    self._get_gradle_command(connector_task, f"-Ds3BuildCachePrefix={self.context.connector.technical_name}"),
                ]
            )
        )
        return await self.get_step_result(gradle_container)
