#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

import json
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import TYPE_CHECKING, Dict

from connector_ops.utils import console  # type: ignore
from jinja2 import Environment, PackageLoader, select_autoescape
from rich.console import Group
from rich.panel import Panel
from rich.style import Style
from rich.table import Table
from rich.text import Text

from pipelines.consts import GCS_PUBLIC_DOMAIN
from pipelines.helpers.github import AIRBYTE_GITHUB_REPO_URL_PREFIX, AIRBYTE_GITHUBUSERCONTENT_URL_PREFIX
from pipelines.helpers.utils import format_duration
from pipelines.models.artifacts import Artifact
from pipelines.models.reports import Report
from pipelines.models.steps import StepStatus

if TYPE_CHECKING:
    from typing import List

    from rich.tree import RenderableType

    from pipelines.airbyte_ci.connectors.context import ConnectorContext


@dataclass(frozen=True)
class ConnectorReport(Report):
    """A dataclass to build connector test reports to share pipelines executions results with the user."""

    pipeline_context: ConnectorContext

    @property
    def report_output_prefix(self) -> str:
        return f"{self.pipeline_context.report_output_prefix}/{self.pipeline_context.connector.technical_name}/{self.pipeline_context.connector.version}"

    @property
    def html_report_file_name(self) -> str:
        return self.filename + ".html"

    def file_remote_storage_key(self, file_name: str) -> str:
        return f"{self.report_output_prefix}/{file_name}"

    @property
    def html_report_remote_storage_key(self) -> str:
        return self.file_remote_storage_key(self.html_report_file_name)

    def file_url(self, file_name: str) -> str:
        return f"{GCS_PUBLIC_DOMAIN}/{self.pipeline_context.ci_report_bucket}/{self.file_remote_storage_key(file_name)}"

    @property
    def html_report_url(self) -> str:
        return self.file_url(self.html_report_file_name)

    def to_json(self) -> str:
        """Create a JSON representation of the connector test report.

        Returns:
            str: The JSON representation of the report.
        """
        assert self.pipeline_context.pipeline_start_timestamp is not None, "The pipeline start timestamp must be set to save reports."

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
                "dagger_cloud_url": self.pipeline_context.dagger_cloud_url,
            }
        )

    def to_html(self) -> str:
        env = Environment(
            loader=PackageLoader("pipelines.airbyte_ci.connectors.test.steps"),
            autoescape=select_autoescape(),
            trim_blocks=False,
            lstrip_blocks=True,
        )
        template = env.get_template("test_report.html.j2")
        template.globals["StepStatus"] = StepStatus
        template.globals["format_duration"] = format_duration
        local_icon_path = Path(f"{self.pipeline_context.connector.code_directory}/icon.svg").resolve()
        step_result_to_artifact_links: Dict[str, List[Dict]] = {}
        for step_result in self.steps_results:
            for artifact in step_result.artifacts:
                if artifact.gcs_url:
                    url = artifact.gcs_url
                elif artifact.local_path:
                    url = artifact.local_path.resolve().as_uri()
                else:
                    continue
                step_result_to_artifact_links.setdefault(step_result.step.title, []).append({"name": artifact.name, "url": url})

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
            "report": self,
            "step_result_to_artifact_links": MappingProxyType(step_result_to_artifact_links),
        }

        if self.pipeline_context.is_ci:
            template_context["commit_url"] = f"{AIRBYTE_GITHUB_REPO_URL_PREFIX}/commit/{self.pipeline_context.git_revision}"
            template_context["gha_workflow_run_url"] = self.pipeline_context.gha_workflow_run_url
            template_context["dagger_logs_url"] = self.pipeline_context.dagger_logs_url
            template_context["dagger_cloud_url"] = self.pipeline_context.dagger_cloud_url
            template_context["icon_url"] = (
                f"{AIRBYTE_GITHUBUSERCONTENT_URL_PREFIX}/{self.pipeline_context.git_revision}/{self.pipeline_context.connector.code_directory}/icon.svg"
            )
        return template.render(template_context)

    async def save_html_report(self) -> None:
        """Save the report as HTML, upload it to GCS if the pipeline is running in CI"""

        html_report_path = self.report_dir_path / self.html_report_file_name
        report_dir = self.pipeline_context.dagger_client.host().directory(str(self.report_dir_path))
        local_html_report_file = report_dir.with_new_file(self.html_report_file_name, self.to_html()).file(self.html_report_file_name)
        html_report_artifact = Artifact(name="HTML Report", content_type="text/html", content=local_html_report_file)
        await html_report_artifact.save_to_local_path(html_report_path)
        absolute_path = html_report_path.absolute()
        self.pipeline_context.logger.info(f"Report saved locally at {absolute_path}")
        if self.pipeline_context.remote_storage_enabled:
            gcs_url = await html_report_artifact.upload_to_gcs(
                dagger_client=self.pipeline_context.dagger_client,
                bucket=self.pipeline_context.ci_report_bucket,  # type: ignore
                key=self.html_report_remote_storage_key,
                gcs_credentials=self.pipeline_context.ci_gcp_credentials,  # type: ignore
            )
            self.pipeline_context.logger.info(f"HTML report uploaded to {gcs_url}")

        elif self.pipeline_context.enable_report_auto_open:
            self.pipeline_context.logger.info("Opening HTML report in browser.")
            webbrowser.open(absolute_path.as_uri())

    async def save(self) -> None:
        await super().save()
        await self.save_html_report()

    def print(self) -> None:
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
        to_render: List[RenderableType] = [step_results_table, details_instructions]

        if self.pipeline_context.dagger_cloud_url:
            self.pipeline_context.logger.info(f"🔗 View runs for commit in Dagger Cloud: {self.pipeline_context.dagger_cloud_url}")

        main_panel = Panel(Group(*to_render), title=main_panel_title, subtitle=duration_subtitle)
        console.print(main_panel)
