#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from __future__ import annotations

import logging
from abc import abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List

import anyio
import asyncer
import click
from dagger import Client, Container, DaggerError

from pipelines import main_logger
from pipelines.helpers import sentry_utils
from pipelines.helpers.utils import format_duration, get_exec_result
from pipelines.models.artifacts import Artifact
from pipelines.models.secrets import Secret

if TYPE_CHECKING:
    from typing import Any, ClassVar, Optional, Set, Union

    import dagger

    from pipelines.models.contexts.pipeline_context import PipelineContext


from abc import ABC

from rich.style import Style

STEP_PARAMS = Dict[str, List[str]]


@dataclass
class MountPath:
    path: Union[Path, str]
    optional: bool = False

    def _cast_fields(self) -> None:
        self.path = Path(self.path)
        self.optional = bool(self.optional)

    def _check_exists(self) -> None:
        if not self.get_path().exists():
            message = f"{self.path} does not exist."
            if self.optional:
                main_logger.warning(message)
            else:
                raise FileNotFoundError(message)

    def get_path(self) -> Path:
        return Path(self.path)

    def __post_init__(self) -> None:
        self._cast_fields()
        self._check_exists()

    def __str__(self) -> str:
        return str(self.path)


@dataclass(kw_only=True, frozen=True)
class Result:
    status: StepStatus
    created_at: datetime = field(default_factory=datetime.utcnow)
    stderr: Optional[str] = None
    stdout: Optional[str] = None
    report: Optional[str] = None
    exc_info: Optional[Exception] = None
    output: Any = None
    artifacts: List[Artifact] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return self.status is StepStatus.SUCCESS


@dataclass(kw_only=True, frozen=True)
class StepResult(Result):
    """A dataclass to capture the result of a step."""

    step: Step
    consider_in_overall_status: bool = True

    def __repr__(self) -> str:  # noqa D105
        return f"{self.step.title}: {self.status.value}"

    def __str__(self) -> str:  # noqa D105
        return f"{self.step.title}: {self.status.value}\n\nSTDOUT:\n{self.stdout}\n\nSTDERR:\n{self.stderr}"

    def __post_init__(self) -> None:
        if self.stderr:
            object.__setattr__(self, "stderr", self.redact_secrets_from_string(self.stderr))
        if self.stdout:
            object.__setattr__(self, "stdout", self.redact_secrets_from_string(self.stdout))

    def redact_secrets_from_string(self, value: str) -> str:
        for secret in self.step.context.secrets_to_mask:
            value = value.replace(secret, "********")
        return value


@dataclass(kw_only=True, frozen=True)
class CommandResult(Result):
    """A dataclass to capture the result of a command."""

    command: click.Command

    def __repr__(self) -> str:  # noqa D105
        return f"{self.command.name}: {self.status.value}"

    def __str__(self) -> str:  # noqa D105
        return f"{self.command.name}: {self.status.value}\n\nSTDOUT:\n{self.stdout}\n\nSTDERR:\n{self.stderr}"


@dataclass(kw_only=True, frozen=True)
class PoeTaskResult(Result):
    task_name: str

    def __repr__(self) -> str:  # noqa D105
        return f"{self.task_name}: {self.status.value}"

    def __str__(self) -> str:  # noqa D105
        return f"{self.task_name}: {self.status.value}\n\nSTDOUT:\n{self.stdout}\n\nSTDERR:\n{self.stderr}"

    def log(self, logger: logging.Logger, verbose: bool = False) -> None:
        """Log the step result.

        Args:
            logger (logging.Logger): The logger to use.
        """
        if self.status is StepStatus.FAILURE:
            logger.exception(self.exc_info)
        else:
            logger.info(f"{self.status.get_emoji()} - Poe {self.task_name} - {self.status.value}")
            if verbose:
                if self.stdout:
                    for line in self.stdout.splitlines():
                        logger.info(line)
                if self.stderr:
                    for line in self.stderr.splitlines():
                        logger.error(line)


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

    def get_github_state(self) -> str:
        """Match state used in the GitHub commit checks to the step status."""
        if self in [StepStatus.SUCCESS, StepStatus.SKIPPED]:
            return "success"
        if self is StepStatus.FAILURE:
            return "failure"
        raise NotImplementedError(f"Unknown state for {self}")

    def __str__(self) -> str:  # noqa D105
        return self.value


class Step(ABC):
    """An abstract class to declare and run pipeline step."""

    max_retries: ClassVar[int] = 0
    max_dagger_error_retries: ClassVar[int] = 3
    should_log: ClassVar[bool] = True
    success_exit_code: ClassVar[int] = 0
    skipped_exit_code: ClassVar[Optional[int]] = None
    # The max duration of a step run. If the step run for more than this duration it will be considered as timed out.
    # The default of 5 hours is arbitrary and can be changed if needed.
    max_duration: ClassVar[timedelta] = timedelta(hours=5)
    retry_delay = timedelta(seconds=10)
    accept_extra_params: bool = False

    def __init__(self, context: PipelineContext, secrets: List[Secret] | None = None) -> None:  # noqa D107
        self.context = context
        self.secrets = secrets if secrets else []
        self.retry_count = 0
        self.started_at: Optional[datetime] = None
        self.stopped_at: Optional[datetime] = None
        self._extra_params: STEP_PARAMS = {}

    @property
    def extra_params(self) -> STEP_PARAMS:
        return self._extra_params

    @extra_params.setter
    def extra_params(self, value: STEP_PARAMS) -> None:
        if value and not self.accept_extra_params:
            raise ValueError(f"{self.__class__.__name__} does not accept extra params.")
        self._extra_params = value
        self.logger.info(f"Will run with the following parameters: {self.params}")

    @property
    def default_params(self) -> STEP_PARAMS:
        return {}

    @property
    def params(self) -> STEP_PARAMS:
        return self.default_params | self.extra_params

    @property
    def params_as_cli_options(self) -> List[str]:
        """Return the step params as a list of CLI options.

        Returns:
            List[str]: The step params as a list of CLI options.
        """
        cli_options: List[str] = []
        for name, values in self.params.items():
            if not values:
                # If no values are available, we assume it is a flag
                cli_options.append(name)
            else:
                cli_options.extend(f"{name}={value}" for value in values)
        return cli_options

    @property
    def title(self) -> str:
        """The title of the step."""
        raise NotImplementedError("Steps must define a 'title' attribute.")

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
    def dagger_client(self) -> Client:
        return self.context.dagger_client

    async def log_progress(self, completion_event: anyio.Event) -> None:
        """Log the step progress every 30 seconds until the step is done."""
        while not completion_event.is_set():
            assert self.started_at is not None, "The step must be started before logging its progress."
            duration = datetime.utcnow() - self.started_at
            elapsed_seconds = duration.total_seconds()
            if elapsed_seconds > 30 and round(elapsed_seconds) % 30 == 0:
                self.logger.info(f"⏳ Still running... (duration: {format_duration(duration)})")
            await anyio.sleep(1)

    async def run_with_completion(self, completion_event: anyio.Event, *args: Any, **kwargs: Any) -> StepResult:
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
    async def run(self, *args: Any, **kwargs: Any) -> StepResult:
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
            step_result = StepResult(step=self, status=StepStatus.FAILURE, stderr=str(e), exc_info=e)

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

    async def retry(self, step_result: StepResult, *args: Any, **kwargs: Any) -> StepResult:
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
    async def _run(self, *args: Any, **kwargs: Any) -> StepResult:
        """Implement the execution of the step and return a step result.

        Returns:
            StepResult: The result of the step run.
        """
        raise NotImplementedError("Steps must define a '_run' attribute.")

    def skip(self, reason: Optional[str] = None) -> StepResult:
        """Declare a step as skipped.

        Args:
            reason (str, optional): Reason why the step was skipped.

        Returns:
            StepResult: A skipped step result.
        """
        return StepResult(step=self, status=StepStatus.SKIPPED, stdout=reason)

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

    async def get_step_result(self, container: Container, *args: Any, **kwargs: Any) -> StepResult:
        """Concurrent retrieval of exit code, stdout and stdout of a container.

        Create a StepResult object from these objects.

        Args:
            container (Container): The container from which we want to infer a step result/

        Returns:
            StepResult: Failure or success with stdout and stderr.
        """
        exit_code, stdout, stderr = await get_exec_result(container)
        return StepResult(
            step=self,
            status=self.get_step_status_from_exit_code(exit_code),
            stderr=stderr,
            stdout=stdout,
            output=container,
        )

    def _get_timed_out_step_result(self) -> StepResult:
        return StepResult(
            step=self,
            status=StepStatus.FAILURE,
            stdout=f"Timed out after the max duration of {format_duration(self.max_duration)}. Please checkout the Dagger logs to see what happened.",
        )


class StepModifyingFiles(Step):
    modified_files: List[str]
    modified_directory: dagger.Directory

    def __init__(self, context: PipelineContext, modified_directory: dagger.Directory, secrets: List[Secret] | None = None) -> None:
        super().__init__(context, secrets)
        self.modified_directory = modified_directory
        self.modified_files = []

    async def export_modified_files(
        self,
        export_to_directory: Path,
    ) -> Set[Path]:
        modified_files = set()
        for modified_file in self.modified_files:
            local_path = export_to_directory / modified_file
            await self.modified_directory.file(str(modified_file)).export(str(local_path))
            modified_files.add(local_path)
        return modified_files
