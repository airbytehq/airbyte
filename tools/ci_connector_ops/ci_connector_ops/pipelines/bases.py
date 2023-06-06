#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module declare base / abstract models to be reused in a pipeline lifecycle."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, ClassVar, List, Optional

import anyio
import asyncer
from anyio import Path
from ci_connector_ops.pipelines.consts import PYPROJECT_TOML_FILE_PATH
from ci_connector_ops.pipelines.utils import check_path_in_workdir, slugify, with_exit_code, with_stderr, with_stdout
from ci_connector_ops.utils import console
from dagger import Container, QueryError
from rich.console import Group
from rich.panel import Panel
from rich.style import Style
from rich.table import Table
from rich.text import Text
from tabulate import tabulate

if TYPE_CHECKING:
    from ci_connector_ops.pipelines.contexts import ConnectorContext, PipelineContext


class CIContext(str, Enum):
    """An enum for Ci context values which can be ["manual", "pull_request", "nightly_builds"]."""

    MANUAL = "manual"
    PULL_REQUEST = "pull_request"
    NIGHTLY_BUILDS = "nightly_builds"
    MASTER = "master"


class StepStatus(Enum):
    """An Enum to characterize the success, failure or skipping of a Step."""

    SUCCESS = "Successful"
    FAILURE = "Failed"
    SKIPPED = "Skipped"

    def from_exit_code(exit_code: int) -> StepStatus:
        """Map an exit code to a step status.

        Args:
            exit_code (int): A process exit code.

        Raises:
            ValueError: Raised if the exit code is not mapped to a step status.

        Returns:
            StepStatus: The step status inferred from the exit code.
        """
        if exit_code == 0:
            return StepStatus.SUCCESS
        # pytest returns a 5 exit code when no test is found.
        elif exit_code == 5:
            return StepStatus.SKIPPED
        else:
            return StepStatus.FAILURE

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
    started_at: ClassVar[datetime]
    retry: ClassVar[bool] = False
    max_retries: ClassVar[int] = 0

    def __init__(self, context: ConnectorContext) -> None:  # noqa D107
        self.context = context
        self.retry_count = 0

    async def run(self, *args, **kwargs) -> StepResult:
        """Public method to run the step. It output a step result.

        If an unexpected dagger error happens it outputs a failed step result with the exception payload.

        Returns:
            StepResult: The step result following the step run.
        """
        self.started_at = datetime.utcnow()
        try:
            result = await self._run(*args, **kwargs)
            if result.status is StepStatus.FAILURE and self.retry_count <= self.max_retries:
                self.retry_count += 1
                await anyio.sleep(10)
                self.context.logger.warn(
                    f"Retry #{self.retry_count} for {self.title} step on connector {self.context.connector.technical_name}"
                )
                return await self.run(*args, **kwargs)
            return result
        except QueryError as e:
            return StepResult(self, StepStatus.FAILURE, stderr=str(e))

    @abstractmethod
    async def _run(self, *args, **kwargs) -> StepResult:
        """Implement the execution of the step and return a step result.

        Returns:
            StepResult: The result of the step run.
        """
        ...

    def skip(self, reason: str = None) -> StepResult:
        """Declare a step as skipped.

        Args:
            reason (str, optional): Reason why the step was skipped.

        Returns:
            StepResult: A skipped step result.
        """
        return StepResult(self, StepStatus.SKIPPED, stdout=reason)

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
        return StepResult(
            self,
            StepStatus.from_exit_code(soon_exit_code.value),
            stderr=soon_stderr.value,
            stdout=soon_stdout.value,
            output_artifact=container,
        )


class PytestStep(Step, ABC):
    """An abstract class to run pytest tests and evaluate success or failure according to pytest logs."""

    async def write_log_file(self, logs) -> str:
        """Return the path to the pytest log file."""
        log_directory = Path(f"{self.context.connector.code_directory}/airbyte_ci_logs")
        await log_directory.mkdir(exist_ok=True)
        await Path(f"{log_directory}/{slugify(self.title).replace('-', '_')}.log").write_text(logs)
        self.context.logger.info(f"Pytest logs written to {log_directory}/{slugify(self.title)}.log")

    # TODO this is not very robust if pytest crashes and does not outputs its expected last log line.
    def pytest_logs_to_step_result(self, logs: str) -> StepResult:
        """Parse pytest log and infer failure, success or skipping.

        Args:
            logs (str): The pytest logs.

        Returns:
            StepResult: The inferred step result according to the log.
        """
        last_log_line = logs.split("\n")[-2]
        if "failed" in last_log_line or "errors" in last_log_line:
            return StepResult(self, StepStatus.FAILURE, stderr=logs)
        elif "no tests ran" in last_log_line:
            return StepResult(self, StepStatus.SKIPPED, stdout=logs)
        else:
            return StepResult(self, StepStatus.SUCCESS, stdout=logs)

    async def _run_tests_in_directory(self, connector_under_test: Container, test_directory: str) -> StepResult:
        """Run the pytest tests in the test_directory that was passed.

        A StepStatus.SKIPPED is returned if no tests were discovered.

        Args:
            connector_under_test (Container): The connector under test container.
            test_directory (str): The directory in which the python test modules are declared

        Returns:
            Tuple[StepStatus, Optional[str], Optional[str]]: Tuple of StepStatus, stderr and stdout.
        """
        test_config = "pytest.ini" if await check_path_in_workdir(connector_under_test, "pytest.ini") else "/" + PYPROJECT_TOML_FILE_PATH
        if await check_path_in_workdir(connector_under_test, test_directory):
            tester = connector_under_test.with_exec(
                [
                    "python",
                    "-m",
                    "pytest",
                    "--suppress-tests-failed-exit-code",
                    "--suppress-no-test-exit-code",
                    "-s",
                    test_directory,
                    "-c",
                    test_config,
                ]
            )
            logs = await tester.stdout()
            if self.context.is_local:
                await self.write_log_file(logs)
            return self.pytest_logs_to_step_result(logs)

        else:
            return StepResult(self, StepStatus.SKIPPED)


@dataclass(frozen=True)
class StepResult:
    """A dataclass to capture the result of a step."""

    step: Step
    status: StepStatus
    created_at: datetime = field(default_factory=datetime.utcnow)
    stderr: Optional[str] = None
    stdout: Optional[str] = None
    output_artifact: Any = None

    def __repr__(self) -> str:  # noqa D105
        return f"{self.step.title}: {self.status.value}"


@dataclass(frozen=True)
class Report:
    """A dataclass to build reports to share pipelines executions results with the user."""

    pipeline_context: PipelineContext
    steps_results: List[StepResult]
    created_at: datetime = field(default_factory=datetime.utcnow)
    name: str = "REPORT"

    @property
    def failed_steps(self) -> List[StepResult]:  # noqa D102
        return [step_result for step_result in self.steps_results if step_result.status is StepStatus.FAILURE]

    @property
    def successful_steps(self) -> List[StepResult]:  # noqa D102
        return [step_result for step_result in self.steps_results if step_result.status is StepStatus.SUCCESS]

    @property
    def skipped_steps(self) -> List[StepResult]:  # noqa D102
        return [step_result for step_result in self.steps_results if step_result.status is StepStatus.SKIPPED]

    @property
    def success(self) -> bool:  # noqa D102
        return len(self.failed_steps) == 0

    @property
    def run_duration(self) -> int:  # noqa D102
        return (self.created_at - self.pipeline_context.created_at).total_seconds()

    def to_json(self) -> str:
        """Create a JSON representation of the report.

        Returns:
            str: The JSON representation of the report.
        """
        return json.dumps(
            {
                "pipeline_name": self.pipeline_context.pipeline_name,
                "run_timestamp": self.created_at.isoformat(),
                "run_duration": self.run_duration,
                "success": self.success,
                "failed_steps": [s.step.__class__.__name__ for s in self.failed_steps],
                "successful_steps": [s.step.__class__.__name__ for s in self.successful_steps],
                "skipped_steps": [s.step.__class__.__name__ for s in self.skipped_steps],
                "gha_workflow_run_url": self.pipeline_context.gha_workflow_run_url,
                "pipeline_start_timestamp": self.pipeline_context.pipeline_start_timestamp,
                "pipeline_end_timestamp": round(self.created_at.timestamp()),
                "pipeline_duration": round(self.created_at.timestamp()) - self.pipeline_context.pipeline_start_timestamp,
                "git_branch": self.pipeline_context.git_branch,
                "git_revision": self.pipeline_context.git_revision,
                "ci_context": self.pipeline_context.ci_context,
                "pull_request_url": self.pipeline_context.pull_request.html_url if self.pipeline_context.pull_request else None,
            }
        )

    def print(self):
        """Print the test report to the console in a nice way."""
        pipeline_name = self.pipeline_context.pipeline_name
        main_panel_title = Text(f"{pipeline_name.upper()} - {self.name}")
        main_panel_title.stylize(Style(color="blue", bold=True))
        duration_subtitle = Text(f"⏲️  Total pipeline duration for {pipeline_name}: {round(self.run_duration)} seconds")
        step_results_table = Table(title="Steps results")
        step_results_table.add_column("Step")
        step_results_table.add_column("Result")
        step_results_table.add_column("Finished after")

        for step_result in self.steps_results:
            step = Text(step_result.step.title)
            step.stylize(step_result.status.get_rich_style())
            result = Text(step_result.status.value)
            result.stylize(step_result.status.get_rich_style())

            if step_result.status is StepStatus.SKIPPED:
                step_results_table.add_row(step, result, "N/A")
            else:
                run_time_seconds = round((step_result.created_at - step_result.step.started_at).total_seconds())
                step_results_table.add_row(step, result, f"{run_time_seconds}s")

        to_render = [step_results_table]
        if self.failed_steps:
            sub_panels = []
            for failed_step in self.failed_steps:
                errors = Text(failed_step.stderr)
                panel_title = Text(f"{pipeline_name} {failed_step.step.title.lower()} failures")
                panel_title.stylize(Style(color="red", bold=True))
                sub_panel = Panel(errors, title=panel_title)
                sub_panels.append(sub_panel)
            failures_group = Group(*sub_panels)
            to_render.append(failures_group)

        main_panel = Panel(Group(*to_render), title=main_panel_title, subtitle=duration_subtitle)
        console.print(main_panel)


@dataclass(frozen=True)
class ConnectorReport(Report):
    """A dataclass to build connector test reports to share pipelines executions results with the user."""

    @property
    def should_be_saved(self) -> bool:  # noqa D102
        return self.pipeline_context.is_ci

    @property
    def should_be_commented_on_pr(self) -> bool:  # noqa D102
        return self.pipeline_context.is_ci and self.pipeline_context.pull_request and self.pipeline_context.PRODUCTION

    def to_json(self) -> str:
        """Create a JSON representation of the connector test report.

        Returns:
            str: The JSON representation of the report.
        """
        return json.dumps(
            {
                "connector_technical_name": self.pipeline_context.connector.technical_name,
                "connector_version": self.pipeline_context.connector.version,
                "run_timestamp": self.created_at.isoformat(),
                "run_duration": self.run_duration,
                "success": self.success,
                "failed_steps": [s.step.__class__.__name__ for s in self.failed_steps],
                "successful_steps": [s.step.__class__.__name__ for s in self.successful_steps],
                "skipped_steps": [s.step.__class__.__name__ for s in self.skipped_steps],
                "gha_workflow_run_url": self.pipeline_context.gha_workflow_run_url,
                "pipeline_start_timestamp": self.pipeline_context.pipeline_start_timestamp,
                "pipeline_end_timestamp": round(self.created_at.timestamp()),
                "pipeline_duration": round(self.created_at.timestamp()) - self.pipeline_context.pipeline_start_timestamp,
                "git_branch": self.pipeline_context.git_branch,
                "git_revision": self.pipeline_context.git_revision,
                "ci_context": self.pipeline_context.ci_context,
                "cdk_version": self.pipeline_context.cdk_version,
            }
        )

    def post_comment_on_pr(self) -> None:
        icon_url = f"https://raw.githubusercontent.com/airbytehq/airbyte/{self.pipeline_context.git_revision}/{self.pipeline_context.connector.code_directory}/icon.svg"
        global_status_emoji = "✅" if self.success else "❌"
        commit_url = f"{self.pipeline_context.pull_request.html_url}/commits/{self.pipeline_context.git_revision}"
        markdown_comment = f'## <img src="{icon_url}" width="40" height="40"> {self.pipeline_context.connector.technical_name} test report (commit [`{self.pipeline_context.git_revision[:10]}`]({commit_url})) - {global_status_emoji}\n\n'
        markdown_comment += f"⏲️  Total pipeline duration: {round(self.run_duration)} seconds\n\n"
        report_data = [
            [step_result.step.title, step_result.status.get_emoji()]
            for step_result in self.steps_results
            if step_result.status is not StepStatus.SKIPPED
        ]
        markdown_comment += tabulate(report_data, headers=["Step", "Result"], tablefmt="pipe") + "\n\n"
        markdown_comment += f"🔗 [View the logs here]({self.pipeline_context.gha_workflow_run_url})\n\n"
        markdown_comment += "*Please note that tests are only run on PR ready for review. Please set your PR to draft mode to not flood the CI engine and upstream service on following commits.*\n"
        markdown_comment += "**You can run the same pipeline locally on this branch with the [airbyte-ci](https://github.com/airbytehq/airbyte/blob/master/tools/ci_connector_ops/ci_connector_ops/pipelines/README.md) tool with the following command**\n"
        markdown_comment += f"```bash\nairbyte-ci connectors --name={self.pipeline_context.connector.technical_name} test\n```\n\n"
        self.pipeline_context.pull_request.create_issue_comment(markdown_comment)

    def print(self):
        """Print the test report to the console in a nice way."""
        connector_name = self.pipeline_context.connector.technical_name
        main_panel_title = Text(f"{connector_name.upper()} - {self.name}")
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
