#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module declare base / abstract models to be reused in a pipeline lifecycle."""

from __future__ import annotations

import json
import typing
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List

import anyio
from anyio import Path
from connector_ops.utils import console
from pipelines.consts import GCS_PUBLIC_DOMAIN, LOCAL_REPORTS_PATH_ROOT
from pipelines.dagger.actions import remote_storage
from pipelines.helpers.utils import format_duration
from pipelines.models.steps import StepResult, StepStatus
from rich.console import Group
from rich.panel import Panel
from rich.style import Style
from rich.table import Table
from rich.text import Text

if typing.TYPE_CHECKING:
    from pipelines.models.steps import PipelineContext


@dataclass(frozen=True)
class Report:
    """A dataclass to build reports to share pipelines executions results with the user."""

    pipeline_context: "PipelineContext"
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
                "dagger_cloud_url": self.pipeline_context.dagger_cloud_url,
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

        if self.pipeline_context.dagger_cloud_url:
            self.pipeline_context.logger.info(f"🔗 View runs for commit in Dagger Cloud: {self.pipeline_context.dagger_cloud_url}")

        main_panel = Panel(Group(*to_render), title=main_panel_title, subtitle=duration_subtitle)
        console.print(main_panel)
