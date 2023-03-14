#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, List, Optional, Union

from ci_connector_ops.utils import console
from dagger import Client, Container
from rich.console import Group
from rich.panel import Panel
from rich.style import Style
from rich.table import Table
from rich.text import Text

if TYPE_CHECKING:
    from ci_connector_ops.pipelines.contexts import ConnectorTestContext


class Step(Enum):
    CODE_FORMAT_CHECKS = "Code format checks"
    PACKAGE_INSTALL = "Package install"
    UNIT_TESTS = "Unit tests"
    INTEGRATION_TESTS = "Integration tests"
    DOCKER_BUILD = "Docker Build"
    ACCEPTANCE_TESTS = "Acceptance tests"
    QA_CHECKS = "QA Checks"

    def get_dagger_pipeline(self, dagger_client_or_container: Union[Client, Container]) -> Union[Client, Container]:
        return dagger_client_or_container.pipeline(self.value)


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


@dataclass(frozen=True)
class StepResult:
    step: Step
    status: StepStatus
    created_at: datetime = field(default_factory=datetime.utcnow)
    stderr: Optional[str] = None
    stdout: Optional[str] = None

    def __repr__(self) -> str:
        return f"{self.step.value}: {self.status.value}"


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
                "failed_step": [failed_step_result.step.name for failed_step_result in self.failed_steps],
                "gha_workflow_run_url": self.connector_test_context.gha_workflow_run_url,
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
            step = Text(step_result.step.value)
            step.stylize(step_result.status.get_rich_style())
            result = Text(step_result.status.value)
            result.stylize(step_result.status.get_rich_style())
            step_results_table.add_row(step, result, str(round((self.created_at - step_result.created_at).total_seconds())) + "s")

        to_render = [step_results_table]
        if self.failed_steps:
            sub_panels = []
            for failed_step in self.failed_steps:
                errors = Text(failed_step.stderr)
                panel_title = Text(f"{connector_name} {failed_step.step.value.lower()} failures")
                panel_title.stylize(Style(color="red", bold=True))
                sub_panel = Panel(errors, title=panel_title)
                sub_panels.append(sub_panel)
            failures_group = Group(*sub_panels)
            to_render.append(failures_group)

        main_panel = Panel(Group(*to_render), title=main_panel_title, subtitle=duration_subtitle)
        console.print(main_panel)
