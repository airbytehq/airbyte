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
from typing import TYPE_CHECKING, Any, ClassVar, Optional, Union

import anyio
import asyncer
import click
from dagger import Container, DaggerError
from pipelines import main_logger
from pipelines.helpers import sentry_utils
from pipelines.helpers.utils import format_duration, get_exec_result

if TYPE_CHECKING:
    from pipelines.models.contexts.pipeline_context import PipelineContext

from abc import ABC

from rich.style import Style


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

    step: Union[Step, click.command]
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


@dataclass(frozen=True)
class CommandResult:
    """A dataclass to capture the result of a command."""

    command: click.command
    status: StepStatus
    created_at: datetime = field(default_factory=datetime.utcnow)
    stderr: Optional[str] = None
    stdout: Optional[str] = None
    exc_info: Optional[Exception] = None

    def __repr__(self) -> str:  # noqa D105
        return f"{self.command.name}: {self.status.value}"

    def __str__(self) -> str:  # noqa D105
        return f"{self.command.name}: {self.status.value}\n\nSTDOUT:\n{self.stdout}\n\nSTDERR:\n{self.stderr}"


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
