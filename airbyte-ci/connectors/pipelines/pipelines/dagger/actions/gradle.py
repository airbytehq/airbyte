#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

from typing import Callable, List, Optional

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
        "docker",  # Required by the integrationTestJava tasks.
        "findutils",  # Gradle requires xargs, which is shipped in findutils.
        "jq",  # Required by the acceptance-test-harness subproject to inspect docker images.
        "rsync",  # Required for gradle cache synchronization.
    ]

    def __init__(
        self,
        dagger_client: dagger.Client,
        gradle_project_dir: dagger.Directory,
        local_execution: bool,
        workdir: str = "/airbyte",
        s3_build_cache_access_key_id: Optional[dagger.Secret] = None,
        s3_build_cache_secret_key: Optional[dagger.Secret] = None,
    ):
        """Initialize a gradle task executor.

        Args:
            dagger_client (dagger.Client): The dagger client.
            gradle_project_dir (dagger.Directory): The gradle project directory to run gradle in.
            local_execution (bool): Whether the gradle task executor is running locally.
            workdir (str, optional): The container path where gradle_project_dir will be mounted. Defaults to "/airbyte".
            s3_build_cache_access_key_id (Optional[dagger.Secret], optional): The S3 build cache access key ID as a dagger secret. Defaults to None.
            s3_build_cache_secret_key (Optional[dagger.Secret], optional): The S3 build cache secret key as a dagger secret. Defaults to None.
        """
        self.dagger_client = dagger_client
        self.gradle_project_dir = gradle_project_dir
        self.local_execution = local_execution
        self.workdir = workdir
        self.s3_build_cache_access_key_id = s3_build_cache_access_key_id
        self.s3_build_cache_secret_key = s3_build_cache_secret_key

    def _s3_build_cache_credentials(self) -> Callable:
        """Closure to set the S3 build cache credentials as environment variables on a gradle container."""

        def wrapper(gradle_container: dagger.Container) -> dagger.Container:
            if self.s3_build_cache_secret_key:
                gradle_container = gradle_container.with_secret_variable("S3_BUILD_CACHE_SECRET_KEY", self.s3_build_cache_secret_key)
            if self.s3_build_cache_access_key_id:
                gradle_container = gradle_container.with_secret_variable("S3_BUILD_CACHE_ACCESS_KEY_ID", self.s3_build_cache_access_key_id)
            return gradle_container

        return wrapper

    def _warm_up_dependency_cache_exec(self) -> List[str]:
        """Commands to execute to warm gradle's dependency cache."""
        # Running a gradle task like "help" with these arguments will trigger updating all dependencies.
        # When the cache is cold, this downloads many gigabytes of jars and poms from all over the internet.
        warm_dependency_cache_args = ["--write-verification-metadata", "sha256", "--dry-run"]
        if self.local_execution:
            # Local dagger engines do not persist cache volumes aggressively like the CI runners do.
            # See https://github.com/airbytehq/airbyte-infra/pull/63 for more details.
            # Downloading all dependencies is also not particularly useful for local development.
            # Therefore, we disable it.
            warm_dependency_cache_args = ["--dry-run"]

        return sh_dash_c(
            [
                # Ensure that the .m2 directory exists.
                f"mkdir -p {self.LOCAL_MAVEN_REPOSITORY_PATH}",
                # Load from the cache volume.
                f"(rsync -a --stats --mkpath {self.GRADLE_DEP_CACHE_PATH}/ {self.GRADLE_HOME_PATH} || true)",
                # Resolve all dependencies and write their checksums to './gradle/verification-metadata.dryrun.xml'.
                self._gradle_command("help", *warm_dependency_cache_args),
                # Build the CDK and publish it to the local maven repository.
                self._gradle_command(":airbyte-cdk:java:airbyte-cdk:publishSnapshotIfNeeded"),
                # Store to the cache volume.
                f"(rsync -a --stats {self.GRADLE_HOME_PATH}/ {self.GRADLE_DEP_CACHE_PATH} || true)",
            ]
        )

    def _gradle_command(self, task: str, *args) -> str:
        """Get the gradlew command to run a given task with the given arguments."""
        return f"./gradlew {' '.join(self.DEFAULT_GRADLE_TASK_OPTIONS + args)} {task}"

    async def __aenter__(self) -> GradleTaskExecutor:
        """Enter the context manager and return a gradle task executor with a gradle container.

        The gradle container is provisioned based on Amazon Corretto image with:
            - Required system dependencies.
            - Environment variables to configure the gradle build cache.
            - A mounted volume to share gradle cache across pipeline runs.
            - A workdir to run gradle in to which the gradle project directory will be mounted.

        Returns:
            GradleTaskExecutor: A gradle task executor with a gradle container.
        """
        dependency_cache_volume = self.dagger_client.cache_volume(self.DEPENDENCY_CACHE_VOLUME_NAME)
        self.gradle_container = await (
            self.dagger_client.container()
            # Use a linux+jdk base image with long-term support, such as amazoncorretto.
            .from_(AMAZONCORRETTO_IMAGE)
            # Mount the dependency cache volume, but not to $GRADLE_HOME, because gradle doesn't expect concurrent modifications.
            .with_mounted_cache(self.GRADLE_DEP_CACHE_PATH, dependency_cache_volume, sharing=dagger.CacheSharingMode.LOCKED)
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
            .with_env_variable("TESTCONTAINERS_RYUK_DISABLED", "true")
            # Set the current working directory.
            .with_workdir(self.workdir)
            # Ensure that the .m2 directory exists.
            .with_exec(["mkdir", "-p", self.LOCAL_MAVEN_REPOSITORY_PATH])
            # Set the S3 build cache credentials.
            # These env vars are consumed by settings.gradle in the repo root.
            .with_(self._s3_build_cache_credentials())
            # Mount the sources.
            .with_mounted_directory(self.workdir, self.gradle_project_dir)
            # Warm the gradle dependency cache.
            .with_exec(self._warm_up_dependency_cache_exec())
        )
        return self

    def run_task(self, task_name: str, *args) -> dagger.Container:
        """Run a gradle task with the given arguments.

        Args:
            task_name (str): The name of the gradle task to run.
            *args: The arguments to pass to the gradle task.

        Returns:
            dagger.Container: The gradle container with the task executed.
        """
        return self.gradle_container.with_exec(sh_dash_c([self._gradle_command(task_name, *args)]))

    async def __aexit__(self, exc_type, exc_value, traceback):
        """Exit the context manager.
        Raises:
            Exception: Any exception raised by the context manager.
        """
        if exc_type is not None:
            raise exc_type(exc_value).with_traceback(traceback) from None
