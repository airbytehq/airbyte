#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from typing import List, Optional, Any, Enum

import anyio
import asyncer
import dagger
import datetime
import logging
from dagger import DaggerError, Container
from pipelines.dagger.actions.python.poetry import with_poetry_module
import pipelines.dagger.actions.system.docker
from pipelines.dagger.containers.python import with_python_base
from pipelines.models.steps import Step, StepResult
from pipelines import main_logger
from pipelines.dagger.actions.python.pipx import with_installed_pipx_package
from pipelines.helpers.utils import format_duration, get_exec_result
from pipelines.models.contexts import PipelineContext



from abc import ABC
from typing import ClassVar, List

from rich.style import Style

from dagger import CacheSharingMode, CacheVolume
from pipelines import hacks
from pipelines.dagger.actions import secrets
from pipelines.consts import AMAZONCORRETTO_IMAGE
from pipelines.helpers.utils import sh_dash_c


@dataclass
class MountPath:
    path: Path
    optional: bool = False

    def _cast_fields(self):
        self.path = Path(self.path)
        self.optional = bool(self.optional)

    def _check_exists(self):
        if not self.path.exists():
            message = f"{self.path} does not exist."
            if self.optional:
                main_logger.warning(message)
            else:
                raise FileNotFoundError(message)

    def __post_init__(self):
        self._cast_fields()
        self._check_exists()

    def __str__(self):
        return str(self.path)

    @property
    def is_file(self) -> bool:
        return self.path.is_file()


@dataclass(frozen=True)
class StepResult:
    """A dataclass to capture the result of a step."""

    step: Step
    status: StepStatus
    created_at: datetime = field(default_factory=datetime.utcnow)
    stderr: Optional[str] = None
    stdout: Optional[str] = None
    output_artifact: Any = None
    exc_info: Optional[Exception] = None

    def __repr__(self) -> str:  # noqa D105
        return f"{self.step.title}: {self.status.value}"

    def __str__(self) -> str:  # noqa D105
        return f"{self.step.title}: {self.status.value}\n\nSTDOUT:\n{self.stdout}\n\nSTDERR:\n{self.stderr}"

    def __post_init__(self):
        if self.stderr:
            super().__setattr__("stderr", self.redact_secrets_from_string(self.stderr))
        if self.stdout:
            super().__setattr__("stdout", self.redact_secrets_from_string(self.stdout))

    def redact_secrets_from_string(self, value: str) -> str:
        for secret in self.step.context.secrets_to_mask:
            value = value.replace(secret, "********")
        return value


class StepStatus(Enum):
    """An Enum to characterize the success, failure or skipping of a Step."""

    SUCCESS = "Successful"
    FAILURE = "Failed"
    SKIPPED = "Skipped"

    def get_rich_style(self) -> Style:
        """Match color used in the console output to the step status."""
        if self is StepStatus.SUCCESS:
            return Style(color="green")
        if self is StepStatus.FAILURE:
            return Style(color="red", bold=True)
        if self is StepStatus.SKIPPED:
            return Style(color="yellow")

    def get_emoji(self) -> str:
        """Match emoji used in the console output to the step status."""
        if self is StepStatus.SUCCESS:
            return "✅"
        if self is StepStatus.FAILURE:
            return "❌"
        if self is StepStatus.SKIPPED:
            return "🟡"

    def __str__(self) -> str:  # noqa D105
        return self.value


class Step(ABC):
    """An abstract class to declare and run pipeline step."""

    title: ClassVar[str]
    max_retries: ClassVar[int] = 0
    max_dagger_error_retries: ClassVar[int] = 3
    should_log: ClassVar[bool] = True
    success_exit_code: ClassVar[int] = 0
    skipped_exit_code: ClassVar[int] = None
    # The max duration of a step run. If the step run for more than this duration it will be considered as timed out.
    # The default of 5 hours is arbitrary and can be changed if needed.
    max_duration: ClassVar[timedelta] = timedelta(hours=5)

    retry_delay = timedelta(seconds=10)

    def __init__(self, context: PipelineContext) -> None:  # noqa D107
        self.context = context
        self.retry_count = 0
        self.started_at = None
        self.stopped_at = None

    @property
    def run_duration(self) -> timedelta:
        if self.started_at and self.stopped_at:
            return self.stopped_at - self.started_at
        else:
            return timedelta(seconds=0)

    @property
    def logger(self) -> logging.Logger:
        if self.should_log:
            return logging.getLogger(f"{self.context.pipeline_name} - {self.title}")
        else:
            disabled_logger = logging.getLogger()
            disabled_logger.disabled = True
            return disabled_logger

    @property
    def dagger_client(self) -> Container:
        return self.context.dagger_client.pipeline(self.title)

    async def log_progress(self, completion_event: anyio.Event) -> None:
        """Log the step progress every 30 seconds until the step is done."""
        while not completion_event.is_set():
            duration = datetime.utcnow() - self.started_at
            elapsed_seconds = duration.total_seconds()
            if elapsed_seconds > 30 and round(elapsed_seconds) % 30 == 0:
                self.logger.info(f"⏳ Still running... (duration: {format_duration(duration)})")
            await anyio.sleep(1)

    async def run_with_completion(self, completion_event: anyio.Event, *args, **kwargs) -> StepResult:
        """Run the step with a timeout and set the completion event when the step is done."""
        try:
            with anyio.fail_after(self.max_duration.total_seconds()):
                result = await self._run(*args, **kwargs)
                completion_event.set()
            return result
        except TimeoutError:
            self.retry_count = self.max_retries + 1
            self.logger.error(f"🚨 {self.title} timed out after {self.max_duration}. No additional retry will happen.")
            completion_event.set()
            return self._get_timed_out_step_result()

    @sentry_utils.with_step_context
    async def run(self, *args, **kwargs) -> StepResult:
        """Public method to run the step. It output a step result.

        If an unexpected dagger error happens it outputs a failed step result with the exception payload.

        Returns:
            StepResult: The step result following the step run.
        """
        self.logger.info(f"🚀 Start {self.title}")
        self.started_at = datetime.utcnow()
        completion_event = anyio.Event()
        try:
            async with asyncer.create_task_group() as task_group:
                soon_result = task_group.soonify(self.run_with_completion)(completion_event, *args, **kwargs)
                task_group.soonify(self.log_progress)(completion_event)
            step_result = soon_result.value
        except DaggerError as e:
            self.logger.error("Step failed with an unexpected dagger error", exc_info=e)
            step_result = StepResult(self, StepStatus.FAILURE, stderr=str(e), exc_info=e)

        self.stopped_at = datetime.utcnow()
        self.log_step_result(step_result)

        lets_retry = self.should_retry(step_result)
        step_result = await self.retry(step_result, *args, **kwargs) if lets_retry else step_result
        return step_result

    def should_retry(self, step_result: StepResult) -> bool:
        """Return True if the step should be retried."""
        if step_result.status is not StepStatus.FAILURE:
            return False
        max_retries = self.max_dagger_error_retries if step_result.exc_info else self.max_retries
        return self.retry_count < max_retries and max_retries > 0

    async def retry(self, step_result, *args, **kwargs) -> StepResult:
        self.retry_count += 1
        self.logger.warn(
            f"Failed with error: {step_result.stderr}.\nRetry #{self.retry_count} in {self.retry_delay.total_seconds()} seconds..."
        )
        await anyio.sleep(self.retry_delay.total_seconds())
        return await self.run(*args, **kwargs)

    def log_step_result(self, result: StepResult) -> None:
        """Log the step result.

        Args:
            result (StepResult): The step result to log.
        """
        duration = format_duration(self.run_duration)
        if result.status is StepStatus.FAILURE:
            self.logger.info(f"{result.status.get_emoji()} failed (duration: {duration})")
        if result.status is StepStatus.SKIPPED:
            self.logger.info(f"{result.status.get_emoji()} was skipped (duration: {duration})")
        if result.status is StepStatus.SUCCESS:
            self.logger.info(f"{result.status.get_emoji()} was successful (duration: {duration})")

    @abstractmethod
    async def _run(self, *args, **kwargs) -> StepResult:
        """Implement the execution of the step and return a step result.

        Returns:
            StepResult: The result of the step run.
        """
        raise NotImplementedError("Steps must define a '_run' attribute.")

    def skip(self, reason: str = None) -> StepResult:
        """Declare a step as skipped.

        Args:
            reason (str, optional): Reason why the step was skipped.

        Returns:
            StepResult: A skipped step result.
        """
        return StepResult(self, StepStatus.SKIPPED, stdout=reason)

    def get_step_status_from_exit_code(
        self,
        exit_code: int,
    ) -> StepStatus:
        """Map an exit code to a step status.

        Args:
            exit_code (int): A process exit code.

        Raises:
            ValueError: Raised if the exit code is not mapped to a step status.

        Returns:
            StepStatus: The step status inferred from the exit code.
        """
        if exit_code == self.success_exit_code:
            return StepStatus.SUCCESS
        elif self.skipped_exit_code is not None and exit_code == self.skipped_exit_code:
            return StepStatus.SKIPPED
        else:
            return StepStatus.FAILURE

    async def get_step_result(self, container: Container) -> StepResult:
        """Concurrent retrieval of exit code, stdout and stdout of a container.

        Create a StepResult object from these objects.

        Args:
            container (Container): The container from which we want to infer a step result/

        Returns:
            StepResult: Failure or success with stdout and stderr.
        """
        exit_code, stdout, stderr = await get_exec_result(container)
        return StepResult(
            self,
            self.get_step_status_from_exit_code(exit_code),
            stderr=stderr,
            stdout=stdout,
            output_artifact=container,
        )

    def _get_timed_out_step_result(self) -> StepResult:
        return StepResult(
            self,
            StepStatus.FAILURE,
            stdout=f"Timed out after the max duration of {format_duration(self.max_duration)}. Please checkout the Dagger logs to see what happened.",
        )


class NoOpStep(Step):
    """A step that does nothing."""

    title = "No Op"
    should_log = False

    def __init__(self, context: PipelineContext, step_status: StepStatus) -> None:
        super().__init__(context)
        self.step_status = step_status

    async def _run(self, *args, **kwargs) -> StepResult:
        return StepResult(self, self.step_status)


class SimpleDockerStep(Step):
    def __init__(
        self,
        title: str,
        context: PipelineContext,
        paths_to_mount: List[MountPath] = [],
        internal_tools: List[MountPath] = [],
        secrets: dict[str, dagger.Secret] = {},
        env_variables: dict[str, str] = {},
        working_directory: str = "/",
        command: Optional[List[str]] = None,
    ):
        """A simple step that runs a given command in a container.

        Args:
            title (str): name of the step
            context (PipelineContext): context of the step
            paths_to_mount (List[MountPath], optional): directory paths to mount. Defaults to [].
            internal_tools (List[MountPath], optional): internal tools to install. Defaults to [].
            secrets (dict[str, dagger.Secret], optional): secrets to add to container. Defaults to {}.
            env_variables (dict[str, str], optional): env variables to set in container. Defaults to {}.
            working_directory (str, optional): working directory to run the command in. Defaults to "/".
            command (Optional[List[str]], optional): The default command to run. Defaults to None.
        """
        self.title = title
        super().__init__(context)

        self.paths_to_mount = paths_to_mount
        self.working_directory = working_directory
        self.internal_tools = internal_tools
        self.secrets = secrets
        self.env_variables = env_variables
        self.command = command

    def _mount_paths(self, container: dagger.Container) -> dagger.Container:
        for path_to_mount in self.paths_to_mount:
            if path_to_mount.optional and not path_to_mount.path.exists():
                continue

            path_string = str(path_to_mount)
            destination_path = f"/{path_string}"
            if path_to_mount.is_file:
                file_to_load = self.context.get_repo_file(path_string)
                container = container.with_mounted_file(destination_path, file_to_load)
            else:
                container = container.with_mounted_directory(destination_path, self.context.get_repo_dir(path_string))
        return container

    async def _install_internal_tools(self, container: dagger.Container) -> dagger.Container:
        for internal_tool in self.internal_tools:
            container = await with_installed_pipx_package(self.context, container, str(internal_tool))
        return container

    def _set_workdir(self, container: dagger.Container) -> dagger.Container:
        return container.with_workdir(self.working_directory)

    def _set_env_variables(self, container: dagger.Container) -> dagger.Container:
        for key, value in self.env_variables.items():
            container = container.with_env_variable(key, value)
        return container

    def _set_secrets(self, container: dagger.Container) -> dagger.Container:
        for key, value in self.secrets.items():
            container = container.with_secret_variable(key, value)
        return container

    async def init_container(self) -> dagger.Container:
        # TODO (ben): Replace with python base container when available
        container = with_python_base(self.context)

        container = self._mount_paths(container)
        container = self._set_env_variables(container)
        container = self._set_secrets(container)
        container = await self._install_internal_tools(container)
        container = self._set_workdir(container)

        return container

    async def _run(self, command=None) -> StepResult:
        command_to_run = command or self.command
        if not command_to_run:
            raise ValueError(f"No command given to the {self.title} step")

        container_to_run = await self.init_container()
        return await self.get_step_result(container_to_run.with_exec(command_to_run))

class PoetryRunStep(Step):
    def __init__(self, context: PipelineContext, title: str, parent_dir_path: str, module_path: str):
        """A simple step that runs a given command inside a poetry project.

        Args:
            context (PipelineContext): context of the step
            title (str): name of the step
            parent_dir_path (str): The path to the parent directory of the poetry project
            module_path (str): The path to the poetry project
        """
        self.title = title
        super().__init__(context)

        parent_dir = self.context.get_repo_dir(parent_dir_path)
        module_path = module_path
        self.poetry_run_container = with_poetry_module(self.context, parent_dir, module_path).with_entrypoint(["poetry", "run"])

    async def _run(self, poetry_run_args: list) -> StepResult:
        poetry_run_exec = self.poetry_run_container.with_exec(poetry_run_args)
        return await self.get_step_result(poetry_run_exec)


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
