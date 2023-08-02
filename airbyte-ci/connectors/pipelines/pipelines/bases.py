#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module declare base / abstract models to be reused in a pipeline lifecycle."""

from __future__ import annotations

import json
import logging
import webbrowser
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import TYPE_CHECKING, Any, ClassVar, List, Optional

import anyio
import asyncer
from anyio import Path
from connector_ops.utils import console
from dagger import Container, DaggerError, QueryError
from jinja2 import Environment, PackageLoader, select_autoescape
from pipelines import sentry_utils
from pipelines.actions import remote_storage
from pipelines.consts import GCS_PUBLIC_DOMAIN, LOCAL_REPORTS_PATH_ROOT, PYPROJECT_TOML_FILE_PATH
from pipelines.utils import check_path_in_workdir, format_duration, get_exec_result
from rich.console import Group
from rich.panel import Panel
from rich.style import Style
from rich.table import Table
from rich.text import Text
from tabulate import tabulate

if TYPE_CHECKING:
    from pipelines.contexts import PipelineContext


class CIContext(str, Enum):
    """An enum for Ci context values which can be ["manual", "pull_request", "nightly_builds"]."""

    MANUAL = "manual"
    PULL_REQUEST = "pull_request"
    NIGHTLY_BUILDS = "nightly_builds"
    MASTER = "master"

    def __str__(self) -> str:
        return self.value


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
    should_log: ClassVar[bool] = True
    success_exit_code: ClassVar[int] = 0
    skipped_exit_code: ClassVar[int] = None
    # The max duration of a step run. If the step run for more than this duration it will be considered as timed out.
    # The default of 5 hours is arbitrary and can be changed if needed.
    max_duration: ClassVar[timedelta] = timedelta(hours=5)

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
        try:
            self.started_at = datetime.utcnow()
            self.logger.info(f"🚀 Start {self.title}")
            completion_event = anyio.Event()
            async with asyncer.create_task_group() as task_group:
                soon_result = task_group.soonify(self.run_with_completion)(completion_event, *args, **kwargs)
                task_group.soonify(self.log_progress)(completion_event)

            result = soon_result.value

            if result.status is StepStatus.FAILURE and self.retry_count <= self.max_retries and self.max_retries > 0:
                self.retry_count += 1
                await anyio.sleep(10)
                self.logger.warn(f"Retry #{self.retry_count}.")
                return await self.run(*args, **kwargs)
            self.stopped_at = datetime.utcnow()
            self.log_step_result(result)
            return result
        except (DaggerError, QueryError) as e:
            self.stopped_at = datetime.utcnow()
            self.logger.error(f"Dagger error on step {self.title}: {e}")
            return StepResult(self, StepStatus.FAILURE, stderr=str(e))

    def log_step_result(self, result: StepResult) -> None:
        """Log the step result.

        Args:
            result (StepResult): The step result to log.
        """
        duration = format_duration(self.run_duration)
        if result.status is StepStatus.FAILURE:
            self.logger.error(f"{result.status.get_emoji()} failed (duration: {duration})")
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
        ...

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


class PytestStep(Step, ABC):
    """An abstract class to run pytest tests and evaluate success or failure according to pytest logs."""

    skipped_exit_code = 5

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
                    "-s",
                    test_directory,
                    "-c",
                    test_config,
                ]
            )
            return await self.get_step_result(tester)

        else:
            return StepResult(self, StepStatus.SKIPPED)


class NoOpStep(Step):
    """A step that does nothing."""

    title = "No Op"
    should_log = False

    def __init__(self, context: PipelineContext, step_status: StepStatus) -> None:
        super().__init__(context)
        self.step_status = step_status

    async def _run(self, *args, **kwargs) -> StepResult:
        return StepResult(self, self.step_status)


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
class Report:
    """A dataclass to build reports to share pipelines executions results with the user."""

    pipeline_context: PipelineContext
    steps_results: List[StepResult]
    created_at: datetime = field(default_factory=datetime.utcnow)
    name: str = "REPORT"
    filename: str = "output"

    @property
    def report_output_prefix(self) -> str:  # noqa D102
        return self.pipeline_context.report_output_prefix

    @property
    def json_report_file_name(self) -> str:  # noqa D102
        return self.filename + ".json"

    @property
    def json_report_remote_storage_key(self) -> str:  # noqa D102
        return f"{self.report_output_prefix}/{self.json_report_file_name}"

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
        return len(self.failed_steps) == 0 and (len(self.skipped_steps) > 0 or len(self.successful_steps) > 0)

    @property
    def run_duration(self) -> timedelta:  # noqa D102
        return self.pipeline_context.stopped_at - self.pipeline_context.started_at

    @property
    def lead_duration(self) -> timedelta:  # noqa D102
        return self.pipeline_context.stopped_at - self.pipeline_context.created_at

    @property
    def remote_storage_enabled(self) -> bool:  # noqa D102
        return self.pipeline_context.is_ci

    async def save_local(self, filename: str, content: str) -> Path:
        """Save the report files locally."""
        local_path = anyio.Path(f"{LOCAL_REPORTS_PATH_ROOT}/{self.report_output_prefix}/{filename}")
        await local_path.parents[0].mkdir(parents=True, exist_ok=True)
        await local_path.write_text(content)
        return local_path

    async def save_remote(self, local_path: Path, remote_key: str, content_type: str = None) -> int:
        gcs_cp_flags = None if content_type is None else [f"--content-type={content_type}"]
        local_file = self.pipeline_context.dagger_client.host().directory(".", include=[str(local_path)]).file(str(local_path))
        report_upload_exit_code, _, _ = await remote_storage.upload_to_gcs(
            dagger_client=self.pipeline_context.dagger_client,
            file_to_upload=local_file,
            key=remote_key,
            bucket=self.pipeline_context.ci_report_bucket,
            gcs_credentials=self.pipeline_context.ci_gcs_credentials_secret,
            flags=gcs_cp_flags,
        )
        gcs_uri = "gs://" + self.pipeline_context.ci_report_bucket + "/" + remote_key
        public_url = f"{GCS_PUBLIC_DOMAIN}/{self.pipeline_context.ci_report_bucket}/{remote_key}"
        if report_upload_exit_code != 0:
            self.pipeline_context.logger.error(f"Uploading {local_path} to {gcs_uri} failed.")
        else:
            self.pipeline_context.logger.info(f"Uploading {local_path} to {gcs_uri} succeeded. Public URL: {public_url}")
        return report_upload_exit_code

    async def save(self) -> None:
        """Save the report files."""
        local_json_path = await self.save_local(self.json_report_file_name, self.to_json())
        absolute_path = await local_json_path.absolute()
        self.pipeline_context.logger.info(f"Report saved locally at {absolute_path}")
        if self.remote_storage_enabled:
            await self.save_remote(local_json_path, self.json_report_remote_storage_key, "application/json")

    def to_json(self) -> str:
        """Create a JSON representation of the report.

        Returns:
            str: The JSON representation of the report.
        """
        return json.dumps(
            {
                "pipeline_name": self.pipeline_context.pipeline_name,
                "run_timestamp": self.pipeline_context.started_at.isoformat(),
                "run_duration": self.run_duration.total_seconds(),
                "success": self.success,
                "failed_steps": [s.step.__class__.__name__ for s in self.failed_steps],
                "successful_steps": [s.step.__class__.__name__ for s in self.successful_steps],
                "skipped_steps": [s.step.__class__.__name__ for s in self.skipped_steps],
                "gha_workflow_run_url": self.pipeline_context.gha_workflow_run_url,
                "pipeline_start_timestamp": self.pipeline_context.pipeline_start_timestamp,
                "pipeline_end_timestamp": round(self.pipeline_context.stopped_at.timestamp()),
                "pipeline_duration": round(self.pipeline_context.stopped_at.timestamp()) - self.pipeline_context.pipeline_start_timestamp,
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
        duration_subtitle = Text(f"⏲️  Total pipeline duration for {pipeline_name}: {format_duration(self.run_duration)}")
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
                run_time = format_duration((step_result.created_at - step_result.step.started_at))
                step_results_table.add_row(step, result, run_time)

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
    def report_output_prefix(self) -> str:  # noqa D102
        return f"{self.pipeline_context.report_output_prefix}/{self.pipeline_context.connector.technical_name}/{self.pipeline_context.connector.version}"

    @property
    def html_report_file_name(self) -> str:  # noqa D102
        return self.filename + ".html"

    @property
    def html_report_remote_storage_key(self) -> str:  # noqa D102
        return f"{self.report_output_prefix}/{self.html_report_file_name}"

    @property
    def html_report_url(self) -> str:  # noqa D102
        return f"{GCS_PUBLIC_DOMAIN}/{self.pipeline_context.ci_report_bucket}/{self.html_report_remote_storage_key}"

    @property
    def should_be_commented_on_pr(self) -> bool:  # noqa D102
        return (
            self.pipeline_context.should_save_report
            and self.pipeline_context.is_ci
            and self.pipeline_context.pull_request
            and self.pipeline_context.PRODUCTION
        )

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
                "run_duration": self.run_duration.total_seconds(),
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
                "html_report_url": self.html_report_url,
            }
        )

    def post_comment_on_pr(self) -> None:
        icon_url = f"https://raw.githubusercontent.com/airbytehq/airbyte/{self.pipeline_context.git_revision}/{self.pipeline_context.connector.code_directory}/icon.svg"
        global_status_emoji = "✅" if self.success else "❌"
        commit_url = f"{self.pipeline_context.pull_request.html_url}/commits/{self.pipeline_context.git_revision}"
        markdown_comment = f'## <img src="{icon_url}" width="40" height="40"> {self.pipeline_context.connector.technical_name} test report (commit [`{self.pipeline_context.git_revision[:10]}`]({commit_url})) - {global_status_emoji}\n\n'
        markdown_comment += f"⏲️  Total pipeline duration: {format_duration(self.run_duration)} \n\n"
        report_data = [
            [step_result.step.title, step_result.status.get_emoji()]
            for step_result in self.steps_results
            if step_result.status is not StepStatus.SKIPPED
        ]
        markdown_comment += tabulate(report_data, headers=["Step", "Result"], tablefmt="pipe") + "\n\n"
        markdown_comment += f"🔗 [View the logs here]({self.html_report_url})\n\n"
        markdown_comment += "*Please note that tests are only run on PR ready for review. Please set your PR to draft mode to not flood the CI engine and upstream service on following commits.*\n"
        markdown_comment += "**You can run the same pipeline locally on this branch with the [airbyte-ci](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connector_ops/connector_ops/pipelines/README.md) tool with the following command**\n"
        markdown_comment += f"```bash\nairbyte-ci connectors --name={self.pipeline_context.connector.technical_name} test\n```\n\n"
        self.pipeline_context.pull_request.create_issue_comment(markdown_comment)

    async def to_html(self) -> str:
        env = Environment(loader=PackageLoader("pipelines.tests"), autoescape=select_autoescape(), trim_blocks=False, lstrip_blocks=True)
        template = env.get_template("test_report.html.j2")
        template.globals["StepStatus"] = StepStatus
        template.globals["format_duration"] = format_duration
        local_icon_path = await Path(f"{self.pipeline_context.connector.code_directory}/icon.svg").resolve()
        template_context = {
            "connector_name": self.pipeline_context.connector.technical_name,
            "step_results": self.steps_results,
            "run_duration": self.run_duration,
            "created_at": self.created_at.isoformat(),
            "connector_version": self.pipeline_context.connector.version,
            "gha_workflow_run_url": None,
            "dagger_logs_url": None,
            "git_branch": self.pipeline_context.git_branch,
            "git_revision": self.pipeline_context.git_revision,
            "commit_url": None,
            "icon_url": local_icon_path.as_uri(),
        }

        if self.pipeline_context.is_ci:
            template_context["commit_url"] = f"https://github.com/airbytehq/airbyte/commit/{self.pipeline_context.git_revision}"
            template_context["gha_workflow_run_url"] = self.pipeline_context.gha_workflow_run_url
            template_context["dagger_logs_url"] = self.pipeline_context.dagger_logs_url
            template_context[
                "icon_url"
            ] = f"https://raw.githubusercontent.com/airbytehq/airbyte/{self.pipeline_context.git_revision}/{self.pipeline_context.connector.code_directory}/icon.svg"
        return template.render(template_context)

    async def save(self) -> None:
        local_html_path = await self.save_local(self.html_report_file_name, await self.to_html())
        absolute_path = await local_html_path.resolve()
        if self.pipeline_context.is_local:
            self.pipeline_context.logger.info(f"HTML report saved locally: {absolute_path}")
            self.pipeline_context.logger.info("Opening HTML report in browser.")
            webbrowser.open(absolute_path.as_uri())
        if self.remote_storage_enabled:
            await self.save_remote(local_html_path, self.html_report_remote_storage_key, "text/html")
            self.pipeline_context.logger.info(f"HTML report uploaded to {self.html_report_url}")
        await super().save()

    def print(self):
        """Print the test report to the console in a nice way."""
        connector_name = self.pipeline_context.connector.technical_name
        main_panel_title = Text(f"{connector_name.upper()} - {self.name}")
        main_panel_title.stylize(Style(color="blue", bold=True))
        duration_subtitle = Text(f"⏲️  Total pipeline duration for {connector_name}: {format_duration(self.run_duration)}")
        step_results_table = Table(title="Steps results")
        step_results_table.add_column("Step")
        step_results_table.add_column("Result")
        step_results_table.add_column("Duration")

        for step_result in self.steps_results:
            step = Text(step_result.step.title)
            step.stylize(step_result.status.get_rich_style())
            result = Text(step_result.status.value)
            result.stylize(step_result.status.get_rich_style())
            step_results_table.add_row(step, result, format_duration(step_result.step.run_duration))

        details_instructions = Text("ℹ️  You can find more details with step executions logs in the saved HTML report.")
        to_render = [step_results_table, details_instructions]

        main_panel = Panel(Group(*to_render), title=main_panel_title, subtitle=duration_subtitle)
        console.print(main_panel)
