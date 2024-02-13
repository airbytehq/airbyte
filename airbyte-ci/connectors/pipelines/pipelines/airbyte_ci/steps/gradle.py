#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from abc import ABC
from datetime import datetime
from pathlib import Path
from typing import Any, ClassVar, List, Optional, Tuple, cast

import pipelines.dagger.actions.system.docker
from dagger import CacheSharingMode, CacheVolume, Container, QueryError
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.consts import AMAZONCORRETTO_IMAGE
from pipelines.dagger.actions import secrets
from pipelines.hacks import never_fail_exec
from pipelines.helpers.utils import sh_dash_c
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

    context: ConnectorContext

    GRADLE_DEP_CACHE_PATH = "/root/gradle-cache"
    GRADLE_HOME_PATH = "/root/.gradle"
    STATIC_GRADLE_OPTIONS = ("--no-daemon", "--no-watch-fs", "--build-cache", "--scan", "--console=plain")
    gradle_task_name: ClassVar[str]
    bind_to_docker_host: ClassVar[bool] = False
    mount_connector_secrets: ClassVar[bool] = False
    with_test_artifacts: ClassVar[bool] = False
    accept_extra_params = True

    @property
    def airbyte_logs_subdir(self) -> str:
        return datetime.fromtimestamp(cast(float, self.context.pipeline_start_timestamp)).isoformat() + "-" + self.gradle_task_name

    @property
    def test_artifacts_path(self) -> Path:
        test_artifacts_path = f"{self.context.connector.code_directory}/build/test-artifacts/{self.airbyte_logs_subdir}"
        return Path(test_artifacts_path)

    @property
    def gradle_task_options(self) -> Tuple[str, ...]:
        return self.STATIC_GRADLE_OPTIONS + (f"-Ds3BuildCachePrefix={self.context.connector.technical_name}",)

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

    def _get_gradle_command(self, task: str, *args: Any, task_options: Optional[List[str]] = None) -> str:
        task_options = task_options or []
        return f"./gradlew {' '.join(self.gradle_task_options + args)} {task} {' '.join(task_options)}"

    async def _run(self, *args: Any, **kwargs: Any) -> StepResult:
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
            # Set the AIRBYTE_LOG_SUBDIR for log4j
            .with_env_variable("AIRBYTE_LOG_SUBDIR", self.airbyte_logs_subdir)
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
        if self.context.s3_build_cache_access_key_id_secret:
            gradle_container_base = gradle_container_base.with_secret_variable(
                "S3_BUILD_CACHE_ACCESS_KEY_ID", self.context.s3_build_cache_access_key_id_secret
            )
            if self.context.s3_build_cache_secret_key_secret:
                gradle_container_base = gradle_container_base.with_secret_variable(
                    "S3_BUILD_CACHE_SECRET_KEY", self.context.s3_build_cache_secret_key_secret
                )

        # Running a gradle task like "help" with these arguments will trigger updating all dependencies.
        # When the cache is cold, this downloads many gigabytes of jars and poms from all over the internet.
        warm_dependency_cache_args = ["--write-verification-metadata", "sha256", "--dry-run"]
        if self.context.is_local:
            # When running locally, this dependency update is slower and less useful than within a CI runner. Skip it.
            warm_dependency_cache_args = ["--dry-run"]

        # Mount the whole git repo to update the cache volume contents.
        with_whole_git_repo = (
            gradle_container_base
            # Mount the whole repo.
            .with_directory("/airbyte", self.context.get_repo_dir("."))
            # Update the cache in place by executing a gradle task which will update all dependencies.
            .with_exec(
                sh_dash_c(
                    [
                        # Defensively delete the gradle home directory to avoid dirtying the cache volume.
                        f"rm -rf {self.GRADLE_HOME_PATH}",
                        # Load from the cache volume.
                        f"(rsync -a --stats --mkpath {self.GRADLE_DEP_CACHE_PATH}/ {self.GRADLE_HOME_PATH} || true)",
                        # Resolve all dependencies and write their checksums to './gradle/verification-metadata.dryrun.xml'.
                        self._get_gradle_command("help", *warm_dependency_cache_args),
                        # Store to the cache volume.
                        f"(rsync -a --stats {self.GRADLE_HOME_PATH}/ {self.GRADLE_DEP_CACHE_PATH} || true)",
                    ]
                )
            )
        )

        # Mount only the code needed to build the connector.
        gradle_container = (
            gradle_container_base
            # Copy the gradle home directory and force evaluation of `with_whole_git_repo` container.
            .with_directory(self.GRADLE_HOME_PATH, await with_whole_git_repo.directory(self.GRADLE_HOME_PATH))
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
        connector_gradle_task = f":airbyte-integrations:connectors:{self.context.connector.technical_name}:{self.gradle_task_name}"
        gradle_command = self._get_gradle_command(connector_gradle_task, task_options=self.params_as_cli_options)
        gradle_container = gradle_container.with_(never_fail_exec([gradle_command]))
        await self._collect_logs(gradle_container)
        await self._collect_test_report(gradle_container)
        return await self.get_step_result(gradle_container)

    async def get_step_result(self, container: Container) -> StepResult:
        step_result = await super().get_step_result(container)
        # Decorate with test report, if applicable.
        return StepResult(
            step=step_result.step,
            status=step_result.status,
            stdout=step_result.stdout,
            stderr=step_result.stderr,
            output_artifact=step_result.output_artifact,
            test_artifacts_path=self.test_artifacts_path,
        )

    async def _collect_logs(self, gradle_container: Container) -> None:
        """
        Exports the java docs from the container into the host filesystem.
        The docs in the container are expected to be in build/test-logs, and will end up test-artifact directory by default
        One can change the destination directory by setting the test_artifacts_path
        """
        if not self.with_test_artifacts:
            return None
        logs_dir_path = f"{self.context.connector.code_directory}/build/test-logs/{self.airbyte_logs_subdir}"
        try:
            container_logs_dir = await gradle_container.directory(logs_dir_path)
            # the gradle task didn't create any logs.
            if not container_logs_dir:
                return None

            self.test_artifacts_path.mkdir(parents=True, exist_ok=True)
            if not await container_logs_dir.export(str(self.test_artifacts_path)):
                self.context.logger.error("Error when trying to export log files from container")
        except QueryError as e:
            self.context.logger.error(str(e))
            self.context.logger.warn(f"Failed to retrieve junit test results from {logs_dir_path} gradle container.")
            return None

    async def _collect_test_report(self, gradle_container: Container) -> None:
        """
        Exports the junit test reports from the container into the host filesystem.
        The docs in the container are expected to be in build/test-results, and will end up test-artifact directory by default
        Only the XML files generated by junit are downloaded into the host filesystem
        One can change the destination directory by setting the test_artifacts_path
        """
        if not self.with_test_artifacts:
            return None

        junit_xml_path = f"{self.context.connector.code_directory}/build/test-results/{self.gradle_task_name}"
        try:
            junit_xml_dir = await gradle_container.directory(junit_xml_path)
            for file_name in await junit_xml_dir.entries():
                if file_name.endswith(".xml"):
                    await junit_xml_dir.file(file_name).export(str(self.test_artifacts_path), allow_parent_dir_path=True)
        except QueryError as e:
            self.context.logger.error(str(e))
            return None
