#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, ClassVar, List, Optional, Union

import asyncer
from ci_connector_ops.pipelines.utils import with_exit_code, with_stderr, with_stdout
from ci_connector_ops.utils import console
from dagger import Client, Container
from rich.console import Group
from rich.panel import Panel
from rich.style import Style
from rich.table import Table
from rich.text import Text

if TYPE_CHECKING:
    from ci_connector_ops.pipelines.contexts import ConnectorTestContext


class StepStatus(Enum):
    SUCCESS = "Successful"
    FAILURE = "Failed"
    SKIPPED = "Skipped"

    def from_exit_code(exit_code: int):
        if exit_code == 0:
            return StepStatus.SUCCESS
        if exit_code == 1:
            return StepStatus.FAILURE
        # pytest returns a 5 exit code when no test is found.
        if exit_code == 5:
            return StepStatus.SKIPPED
        else:
            raise ValueError(f"No step status is mapped to exit code {exit_code}")

    def get_rich_style(self) -> Style:
        if self is StepStatus.SUCCESS:
            return Style(color="green")
        if self is StepStatus.FAILURE:
            return Style(color="red", bold=True)
        if self is StepStatus.SKIPPED:
            return Style(color="yellow")

    def __str__(self) -> str:
        return self.value


class Step(ABC):
    title: ClassVar

    def __init__(self, context: ConnectorTestContext) -> None:
        self.context = context

    @abstractmethod
    async def run(self) -> StepResult:
        """Run the step and output a step result.

        Returns:
            StepResult: The result of the step run.
        """
        ...

    def skip(self, reason: str = None) -> StepResult:
        return StepResult(self, StepStatus.SKIPPED, stdout=reason)

    def get_dagger_pipeline(self, dagger_client_or_container: Union[Client, Container]) -> Union[Client, Container]:
        return dagger_client_or_container.pipeline(self.title)

    async def get_step_result(self, container: Container) -> StepResult:
        """Concurrent retrieval of exit code, stdout and stdout of a container.
        Create a StepResult object from these objects.

        Args:
            container (Container): The container from which we want to infer a step result/

        Returns:
            StepResult: Failure or success with stdout and stderr.
        """
        async with asyncer.create_task_group() as task_group:
            soon_exit_code = task_group.soonify(with_exit_code)(container)
            soon_stderr = task_group.soonify(with_stderr)(container)
            soon_stdout = task_group.soonify(with_stdout)(container)
        return StepResult(self, StepStatus.from_exit_code(soon_exit_code.value), stderr=soon_stderr.value, stdout=soon_stdout.value)


@dataclass(frozen=True)
class StepResult:
    step: Step
    status: StepStatus
    created_at: datetime = field(default_factory=datetime.utcnow)
    stderr: Optional[str] = None
    stdout: Optional[str] = None

    def __repr__(self) -> str:
        return f"{self.step.title}: {self.status.value}"


@dataclass(frozen=True)
class ConnectorTestReport:
    connector_test_context: ConnectorTestContext
    steps_results: List[StepResult]
    created_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def failed_steps(self) -> StepResult:
        return [step_result for step_result in self.steps_results if step_result.status is StepStatus.FAILURE]

    @property
    def success(self) -> StepResult:
        return len(self.failed_steps) == 0

    @property
    def should_be_saved(self) -> bool:
        return self.connector_test_context.is_ci

    @property
    def run_duration(self) -> int:
        return (self.created_at - self.connector_test_context.created_at).total_seconds()

    def to_json(self) -> str:
        return json.dumps(
            {
                "connector_technical_name": self.connector_test_context.connector.technical_name,
                "connector_version": self.connector_test_context.connector.version,
                "run_timestamp": self.created_at.isoformat(),
                "run_duration": self.run_duration,
                "success": self.success,
                "failed_step": [failed_step_result.step.__class__.__name__ for failed_step_result in self.failed_steps],
                "gha_workflow_run_url": self.connector_test_context.gha_workflow_run_url,
                "pipeline_start_timestamp": self.connector_test_context.pipeline_start_timestamp,
                "pipeline_end_timestamp": round(self.created_at.timestamp()),
                "pipeline_duration": round(self.created_at.timestamp()) - self.connector_test_context.pipeline_start_timestamp,
                "git_branch": self.connector_test_context.git_branch,
                "git_revision": self.connector_test_context.git_revision,
                "ci_context": self.connector_test_context.ci_context,
            }
        )

    def print(self):
        connector_name = self.connector_test_context.connector.technical_name
        main_panel_title = Text(f"{connector_name.upper()} - TEST RESULTS")
        main_panel_title.stylize(Style(color="blue", bold=True))
        duration_subtitle = Text(f"⏲️  Total pipeline duration for {connector_name}: {round(self.run_duration)} seconds")
        step_results_table = Table(title="Steps results")
        step_results_table.add_column("Step")
        step_results_table.add_column("Result")
        step_results_table.add_column("Finished after")

        for step_result in self.steps_results:
            step = Text(step_result.step.title)
            step.stylize(step_result.status.get_rich_style())
            result = Text(step_result.status.value)
            result.stylize(step_result.status.get_rich_style())
            step_results_table.add_row(step, result, f"{round((self.created_at - step_result.created_at).total_seconds())}s")

        to_render = [step_results_table]
        if self.failed_steps:
            sub_panels = []
            for failed_step in self.failed_steps:
                errors = Text(failed_step.stderr)
                panel_title = Text(f"{connector_name} {failed_step.step.title.lower()} failures")
                panel_title.stylize(Style(color="red", bold=True))
                sub_panel = Panel(errors, title=panel_title)
                sub_panels.append(sub_panel)
            failures_group = Group(*sub_panels)
            to_render.append(failures_group)

        main_panel = Panel(Group(*to_render), title=main_panel_title, subtitle=duration_subtitle)
        console.print(main_panel)
