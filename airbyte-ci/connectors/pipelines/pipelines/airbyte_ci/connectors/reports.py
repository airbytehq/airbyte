#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

import json
import webbrowser
from dataclasses import dataclass
from typing import TYPE_CHECKING

from anyio import Path
from connector_ops.utils import console  # type: ignore
from jinja2 import Environment, PackageLoader, select_autoescape
from pipelines.consts import GCS_PUBLIC_DOMAIN
from pipelines.helpers.utils import format_duration
from pipelines.models.reports import Report
from pipelines.models.steps import StepStatus
from rich.console import Group
from rich.panel import Panel
from rich.style import Style
from rich.table import Table
from rich.text import Text

if TYPE_CHECKING:
    from typing import List

    from pipelines.airbyte_ci.connectors.context import ConnectorContext
    from rich.tree import RenderableType


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

    @property
    def html_report_remote_storage_key(self) -> str:
        return f"{self.report_output_prefix}/{self.html_report_file_name}"

    @property
    def html_report_url(self) -> str:
        return f"{GCS_PUBLIC_DOMAIN}/{self.pipeline_context.ci_report_bucket}/{self.html_report_remote_storage_key}"

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
                "failed_steps": [s.step.__class__.__name__ for s in self.failed_steps],  # type: ignore
                "successful_steps": [s.step.__class__.__name__ for s in self.successful_steps],  # type: ignore
                "skipped_steps": [s.step.__class__.__name__ for s in self.skipped_steps],  # type: ignore
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

    async def to_html(self) -> str:
        env = Environment(
            loader=PackageLoader("pipelines.airbyte_ci.connectors.test.steps"),
            autoescape=select_autoescape(),
            trim_blocks=False,
            lstrip_blocks=True,
        )
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
            template_context["dagger_cloud_url"] = self.pipeline_context.dagger_cloud_url
            template_context[
                "icon_url"
            ] = f"https://raw.githubusercontent.com/airbytehq/airbyte/{self.pipeline_context.git_revision}/{self.pipeline_context.connector.code_directory}/icon.svg"
        return template.render(template_context)

    async def save(self) -> None:
        local_html_path = await self.save_local(self.html_report_file_name, await self.to_html())
        absolute_path = await local_html_path.resolve()
        if self.pipeline_context.enable_report_auto_open:
            self.pipeline_context.logger.info(f"HTML report saved locally: {absolute_path}")
            if self.pipeline_context.enable_report_auto_open:
                self.pipeline_context.logger.info("Opening HTML report in browser.")
                webbrowser.open(absolute_path.as_uri())
        if self.remote_storage_enabled:
            await self.save_remote(local_html_path, self.html_report_remote_storage_key, "text/html")
            self.pipeline_context.logger.info(f"HTML report uploaded to {self.html_report_url}")
        await super().save()

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
