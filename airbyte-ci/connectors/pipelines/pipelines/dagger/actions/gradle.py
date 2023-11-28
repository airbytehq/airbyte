#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

from typing import Callable, Optional, Tuple

import dagger
from pipelines.consts import AMAZONCORRETTO_IMAGE
from pipelines.helpers.utils import sh_dash_c


class GradleTaskExecutor:
    """A context manager to run gradle tasks in a container with a gradle cache persistence."""

    DEFAULT_GRADLE_TASK_OPTIONS = ("--no-daemon", "--no-watch-fs", "--scan", "--build-cache", "--console=plain")
    DEPENDENCY_CACHE_VOLUME_NAME = "gradle-dependency-cache"
    GRADLE_DEP_CACHE_PATH = "/root/gradle-cache"
    GRADLE_HOME_PATH = "/root/.gradle"
    LOCAL_MAVEN_REPOSITORY_PATH = "/root/.m2"
    YUM_PACKAGES_TO_INSTALL = [
        "docker",  # required by :integrationTestJava.
        "findutils",  # gradle requires xargs, which is shipped in findutils.
        "jq",  # required by :acceptance-test-harness to inspect docker images.
        "rsync",  # required for gradle cache synchronization.
    ]

    def __init__(
        self,
        dagger_client: dagger.Client,
        gradle_project_dir: dagger.Directory,
        local_execution: bool,
        build_cdk: bool = False,
        export_gradle_project_directory_to_host: bool = False,
        export_gradle_project_directory_to_host_path: str = ".",
        workdir: str = "/airbyte",
        s3_build_cache_access_key_id: Optional[dagger.Secret] = None,
        s3_build_cache_secret_key: Optional[dagger.Secret] = None,
    ):
        """Initialize a gradle task executor.

        Args:
            dagger_client (dagger.Client): The dagger client.
            gradle_project_dir (dagger.Directory): The gradle project directory to run gradle in.
            local_execution (bool): Whether the gradle task executor is running locally.
            build_cdk (bool): Whether to build and publish the local CDK if needed. Defaults to False.
            export_gradle_project_directory_to_host (bool, optional): Whether to export the gradle project directory to the host on context exit. Defaults to False.
            export_gradle_project_directory_to_host_path (str, optional): The path to where the gradle project directory will be exported on the host filesystem. Defaults to ".".
            workdir (str, optional): The container path where gradle_project_dir will be mounted. Defaults to "/airbyte".
            s3_build_cache_access_key_id (Optional[dagger.Secret], optional): The S3 build cache access key ID as a dagger secret. Defaults to None.
            s3_build_cache_secret_key (Optional[dagger.Secret], optional): The S3 build cache secret key as a dagger secret. Defaults to None.
        """
        self.dagger_client = dagger_client
        self.gradle_project_dir = gradle_project_dir
        self.local_execution = local_execution
        self.build_cdk = build_cdk
        self.export_gradle_project_directory_to_host = export_gradle_project_directory_to_host
        self.export_gradle_project_directory_to_host_path = export_gradle_project_directory_to_host_path
        self.workdir = workdir
        self.s3_build_cache_access_key_id = s3_build_cache_access_key_id
        self.s3_build_cache_secret_key = s3_build_cache_secret_key

    @property
    def dependency_cache_volume(self) -> dagger.CacheVolume:
        """This cache volume is for sharing gradle dependencies (jars and poms) across all pipeline runs."""
        return self.dagger_client.cache_volume(self.DEPENDENCY_CACHE_VOLUME_NAME)

    def get_base_gradle_container(self) -> dagger.Container:
        """Provision a gradle container based on Amazon Corretto image with:
            - Required system dependencies.
            - Environment variables to configure the gradle build cache.
            - A mounted volume to share gradle cache across pipeline runs.
            - A workdir to run gradle in to which the gradle project directory will be mounted.
        Returns:
            dagger.Container: The base gradle container.
        """
        return (
            self.dagger_client.container()
            # Use a linux+jdk base image with long-term support, such as amazoncorretto.
            .from_(AMAZONCORRETTO_IMAGE)
            # Mount the dependency cache volume, but not to $GRADLE_HOME, because gradle doesn't expect concurrent modifications.
            .with_mounted_cache(self.GRADLE_DEP_CACHE_PATH, self.dependency_cache_volume, sharing=dagger.CacheSharingMode.LOCKED)
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
                        f"yum install -y {' '.join(self.YUM_PACKAGES_TO_INSTALL)}",
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
            .with_env_variable("TESTCONTAINERS_RYUK_DISABLED", "true").with_workdir(self.workdir)
            # Ensure that the .m2 directory exists.
            .with_exec(["mkdir", "-p", self.LOCAL_MAVEN_REPOSITORY_PATH])
        )

    @staticmethod
    def set_s3_build_cache_credentials(
        s3_build_cache_access_key_id: Optional[dagger.Secret], s3_build_cache_secret_key: Optional[dagger.Secret]
    ) -> Callable:
        """Closure to set the S3 build cache credentials as environment variables on a gradle container.

        Args:
            s3_build_cache_access_key_id (Optional[dagger.Secret]): The S3 build cache access key ID as a dagger secret.
            s3_build_cache_secret_key (Optional[dagger.Secret]): The S3 build cache secret key as a dagger secret.

        Returns:
            Callable: A function which takes a gradle container and returns a gradle container with the S3 build cache credentials set as environment variables.
        """

        def wrapper(gradle_container: dagger.Container) -> dagger.Container:
            if s3_build_cache_access_key_id:
                gradle_container = gradle_container.with_secret_variable("S3_BUILD_CACHE_ACCESS_KEY_ID", s3_build_cache_access_key_id)
            if s3_build_cache_secret_key:
                gradle_container = gradle_container.with_secret_variable("S3_BUILD_CACHE_SECRET_KEY", s3_build_cache_secret_key)
            return gradle_container

        return wrapper

    def warm_up_dependency_cache(
        self, gradle_dep_cache_path: str, gradle_home_path: str, build_cdk: bool, warm_dependency_cache_args: Tuple[str] = ("--dry-run")
    ) -> Callable:
        """Closure to seed the gradle home cache from the cache volume.
        Args:
            gradle_dep_cache_path (str): The path to the gradle dependency cache volume mount.
            gradle_home_path (str): The path to the gradle home directory.
            build_cdk (bool): Whether to build the CDK.
            local_maven_repository_path (str): The path to the local maven repository.

        Returns:
            Callable: A function which takes a gradle container and returns a gradle container with the gradle cache seeded from the volume.
        """

        rsync_cache_volume_to_gradle_home = f"(rsync -a --stats --mkpath {gradle_dep_cache_path}/ {gradle_home_path} || true)"
        rsync_gradle_home_to_cache_volume = f"(rsync -a --stats {self.GRADLE_HOME_PATH}/ {self.GRADLE_DEP_CACHE_PATH} || true)"
        # Running a gradle task like "help" with these arguments will trigger updating all dependencies.
        # When the cache is cold, this downloads many gigabytes of jars and poms from all over the internet.
        resolve_deps_and_write_checksum = self._get_gradle_command("help", *warm_dependency_cache_args)
        build_and_publish_local_cdk = self._get_gradle_command(":airbyte-cdk:java:airbyte-cdk:publishSnapshotIfNeeded")

        gradle_commands = [resolve_deps_and_write_checksum]
        if build_cdk:
            gradle_commands.append(build_and_publish_local_cdk)

        commands = [
            rsync_cache_volume_to_gradle_home,
            *gradle_commands,
            rsync_gradle_home_to_cache_volume,
        ]

        def wrapper(gradle_container: dagger.Container) -> dagger.Container:
            return gradle_container.with_exec(sh_dash_c(commands))

        return wrapper

    def _get_gradle_command(self, task: str, *args) -> str:
        """Get the gradlew command to run a given task with the given arguments."""
        return f"./gradlew {' '.join(self.DEFAULT_GRADLE_TASK_OPTIONS + args)} {task}"

    async def __aenter__(self) -> GradleTaskExecutor:
        """Enter the context manager and return a gradle task executor with a base gradle container with a seeded cache and S3 build cache set up.

        Returns:
            GradleTaskExecutor: A gradle task executor with a base gradle container.
        """
        warm_dependency_cache_args = ["--write-verification-metadata", "sha256", "--dry-run"] if not self.local_execution else ["--dry-run"]

        self.gradle_container = await (
            self.get_base_gradle_container()
            .with_(self.set_s3_build_cache_credentials(self.s3_build_cache_access_key_id, self.s3_build_cache_secret_key))
            .with_mounted_directory(self.workdir, self.gradle_project_dir)
            .with_(
                self.warm_up_dependency_cache(self.GRADLE_DEP_CACHE_PATH, self.GRADLE_HOME_PATH, self.build_cdk, warm_dependency_cache_args)
            )
        )

        return self

    async def run_task(self, task_name: str, *args) -> dagger.Container:
        """Run a gradle task with the given arguments.

        Args:
            task_name (str): The name of the gradle task to run.
            *args: The arguments to pass to the gradle task.

        Raises:
            Exception: If gradlew is not found in the current directory.

        Returns:
            dagger.Container: The gradle container with the task executed.
        """
        if "gradlew" not in await self.gradle_container.directory(".").entries():
            raise Exception("gradlew not found in the current directory, please mount a directory with gradlew to the container.")
        self.gradle_container = self.gradle_container.with_exec(sh_dash_c([self._get_gradle_command(task_name, *args)]))
        return self.gradle_container

    async def _export_gradle_project_directory_to_host(self, host_dir_path: str) -> None:
        """Export the gradle project directory to the host.

        Args:
            host_dir_path (str, optional): Path to where the gradle project directory will be exported on the host filesystem.

        """
        await self.gradle_container.directory(self.workdir).export(host_dir_path)

    async def __aexit__(self, exc_type, exc_value, traceback):
        """Exit the context manager.
        Raises:
            Exception: Any exception raised by the context manager.
        """
        if exc_type is not None:
            raise exc_type(exc_value).with_traceback(traceback) from None
        if self.export_gradle_project_directory_to_host:
            await self._export_gradle_project_directory_to_host(self.export_gradle_project_directory_to_host_path)
