#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module declare base / abstract models to be reused in a pipeline lifecycle."""

from __future__ import annotations

import json
import time
import typing
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import List

from connector_ops.utils import console  # type: ignore
from pipelines.consts import LOCAL_REPORTS_PATH_ROOT
from pipelines.helpers.utils import format_duration, slugify
from pipelines.models.artifacts import Artifact
from pipelines.models.steps import StepResult, StepStatus
from rich.console import Group
from rich.panel import Panel
from rich.style import Style
from rich.table import Table
from rich.text import Text

if typing.TYPE_CHECKING:
    from pipelines.models.contexts.pipeline_context import PipelineContext
    from rich.tree import RenderableType


@dataclass(frozen=True)
class Report:
    """A dataclass to build reports to share pipelines executions results with the user."""

    pipeline_context: PipelineContext
    steps_results: List[StepResult]
    created_at: datetime = field(default_factory=datetime.utcnow)
    name: str = "REPORT"
    filename: str = "output"

    @property
    def report_output_prefix(self) -> str:
        return self.pipeline_context.report_output_prefix

    @property
    def report_dir_path(self) -> Path:
        return Path(f"{LOCAL_REPORTS_PATH_ROOT}/{self.report_output_prefix}")

    @property
    def json_report_file_name(self) -> str:
        return self.filename + ".json"

    @property
    def json_report_remote_storage_key(self) -> str:
        return f"{self.report_output_prefix}/{self.json_report_file_name}"

    @property
    def failed_steps(self) -> List[StepResult]:
        return [step_result for step_result in self.steps_results if step_result.status is StepStatus.FAILURE]

    @property
    def successful_steps(self) -> List[StepResult]:
        return [step_result for step_result in self.steps_results if step_result.status is StepStatus.SUCCESS]

    @property
    def skipped_steps(self) -> List[StepResult]:
        return [step_result for step_result in self.steps_results if step_result.status is StepStatus.SKIPPED]

    @property
    def success(self) -> bool:
        return len(self.failed_steps) == 0 and (len(self.skipped_steps) > 0 or len(self.successful_steps) > 0)

    @property
    def run_duration(self) -> timedelta:
        assert self.pipeline_context.started_at is not None, "The pipeline started_at timestamp must be set to save reports."
        assert self.pipeline_context.stopped_at is not None, "The pipeline stopped_at timestamp must be set to save reports."
        return self.pipeline_context.stopped_at - self.pipeline_context.started_at

    @property
    def lead_duration(self) -> timedelta:
        assert self.pipeline_context.started_at is not None, "The pipeline started_at timestamp must be set to save reports."
        assert self.pipeline_context.stopped_at is not None, "The pipeline stopped_at timestamp must be set to save reports."
        return self.pipeline_context.stopped_at - self.pipeline_context.created_at

    async def save(self) -> None:
        self.report_dir_path.mkdir(parents=True, exist_ok=True)
        await self.save_json_report()
        await self.save_step_result_artifacts()

    async def save_json_report(self) -> None:
        """Save the report as JSON, upload it to GCS if the pipeline is running in CI"""

        json_report_path = self.report_dir_path / self.json_report_file_name
        report_dir = self.pipeline_context.dagger_client.host().directory(str(self.report_dir_path))
        local_json_report_file = report_dir.with_new_file(self.json_report_file_name, self.to_json()).file(self.json_report_file_name)
        json_report_artifact = Artifact(name="JSON Report", content_type="application/json", content=local_json_report_file)
        await json_report_artifact.save_to_local_path(json_report_path)
        absolute_path = json_report_path.absolute()
        self.pipeline_context.logger.info(f"Report saved locally at {absolute_path}")
        if self.pipeline_context.remote_storage_enabled:
            gcs_url = await json_report_artifact.upload_to_gcs(
                dagger_client=self.pipeline_context.dagger_client,
                bucket=self.pipeline_context.ci_report_bucket,  # type: ignore
                key=self.json_report_remote_storage_key,
                gcs_credentials=self.pipeline_context.ci_gcp_credentials,  # type: ignore
            )
            self.pipeline_context.logger.info(f"JSON Report uploaded to {gcs_url}")
        else:
            self.pipeline_context.logger.info("JSON Report not uploaded to GCS because remote storage is disabled.")

    async def save_step_result_artifacts(self) -> None:
        local_artifacts_dir = self.report_dir_path / "artifacts"
        local_artifacts_dir.mkdir(parents=True, exist_ok=True)
        # TODO: concurrent save and upload
        for step_result in self.steps_results:
            for artifact in step_result.artifacts:
                step_artifacts_dir = local_artifacts_dir / slugify(step_result.step.title)
                step_artifacts_dir.mkdir(parents=True, exist_ok=True)
                await artifact.save_to_local_path(step_artifacts_dir / artifact.name)
                if self.pipeline_context.remote_storage_enabled:
                    upload_time = int(time.time())
                    gcs_url = await artifact.upload_to_gcs(
                        dagger_client=self.pipeline_context.dagger_client,
                        bucket=self.pipeline_context.ci_report_bucket,  # type: ignore
                        key=f"{self.report_output_prefix}/artifacts/{slugify(step_result.step.title)}/{upload_time}_{artifact.name}",
                        gcs_credentials=self.pipeline_context.ci_gcp_credentials,  # type: ignore
                    )
                    self.pipeline_context.logger.info(f"Artifact {artifact.name} for {step_result.step.title} uploaded to {gcs_url}")
                else:
                    self.pipeline_context.logger.info(
                        f"Artifact {artifact.name} for {step_result.step.title} not uploaded to GCS because remote storage is disabled."
                    )

    def to_json(self) -> str:
        """Create a JSON representation of the report.

        Returns:
            str: The JSON representation of the report.
        """
        assert self.pipeline_context.pipeline_start_timestamp is not None, "The pipeline start timestamp must be set to save reports."
        assert self.pipeline_context.started_at is not None, "The pipeline started_at timestamp must be set to save reports."
        assert self.pipeline_context.stopped_at is not None, "The pipeline stopped_at timestamp must be set to save reports."
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

    def print(self) -> None:
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
                assert step_result.step.started_at is not None, "The step started_at timestamp must be set to print reports."
                run_time = format_duration((step_result.created_at - step_result.step.started_at))
                step_results_table.add_row(step, result, run_time)

        to_render: List[RenderableType] = [step_results_table]
        if self.failed_steps:
            sub_panels = []
            for failed_step in self.failed_steps:
                errors = Text(failed_step.stderr) if failed_step.stderr else Text("")
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
