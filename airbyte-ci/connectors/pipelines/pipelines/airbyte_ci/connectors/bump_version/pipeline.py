#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from typing import TYPE_CHECKING

from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.airbyte_ci.connectors.reports import ConnectorReport, Report
from pipelines.airbyte_ci.steps.bump_version import BumpConnectorVersion
from pipelines.airbyte_ci.steps.changelog import AddChangelogEntry
from pipelines.models.steps import Step, StepResult, StepStatus

if TYPE_CHECKING:
    from anyio import Semaphore


class RestoreVersionState(Step):
    context: ConnectorContext

    title = "Restore original version state"

    def __init__(self, context: ConnectorContext) -> None:
        super().__init__(context)
        connector = context.connector
        if connector.metadata_file_path.is_file():
            self.metadata_content = connector.metadata_file_path.read_text()
        else:
            self.metadata_content = None

        if connector.dockerfile_file_path.is_file():
            self.dockerfile_content = connector.dockerfile_file_path.read_text()
        else:
            self.dockerfile_content = None

        if connector.pyproject_file_path.is_file():
            self.poetry_content = connector.pyproject_file_path.read_text()
        else:
            self.poetry_content = None

        if connector.documentation_file_path and connector.documentation_file_path.is_file():
            self.documentation_content = connector.documentation_file_path.read_text()
        else:
            self.documentation_content = None

    async def _run(self) -> StepResult:
        connector = self.context.connector
        if self.metadata_content:
            connector.metadata_file_path.write_text(self.metadata_content)
        if self.dockerfile_content:
            connector.dockerfile_file_path.write_text(self.dockerfile_content)
        if self.poetry_content:
            connector.pyproject_file_path.write_text(self.poetry_content)
        if self.documentation_content and connector.documentation_file_path:
            connector.documentation_file_path.write_text(self.documentation_content)
        return StepResult(step=self, status=StepStatus.SUCCESS)

    async def _cleanup(self) -> StepResult:
        return StepResult(step=self, status=StepStatus.SUCCESS)


async def run_connector_version_bump_pipeline(
    context: ConnectorContext,
    semaphore: "Semaphore",
    bump_type: str,
    changelog_entry: str,
    pull_request_number: str | int | None = None,
) -> Report:
    """Run a pipeline to upgrade for a single connector.

    Args:
        context (ConnectorContext): The initialized connector context.

    Returns:
        Report: The reports holding the base image version upgrade results.
    """
    report_name = "CONNECTOR VERSION BUMP RESULTS"
    async with semaphore:
        steps_results = []
        async with context:
            bump_version = BumpConnectorVersion(context, bump_type)
            bump_version_result = await bump_version.run()
            steps_results.append(bump_version_result)
            if not bump_version_result.success:
                report = ConnectorReport(context, steps_results, name=report_name)
                context.report = report
                return report

            updated_connector_directory = bump_version_result.output
            for modified_file in bump_version.modified_files:
                await updated_connector_directory.file(modified_file).export(str(context.connector.code_directory / modified_file))
                context.logger.info(f"Exported {modified_file} following the version bump.")

            add_changelog_entry = AddChangelogEntry(
                context, bump_version.new_version, changelog_entry, pull_request_number=pull_request_number
            )
            add_changelog_entry_result = await add_changelog_entry.run()
            steps_results.append(add_changelog_entry_result)
            if not add_changelog_entry_result.success:
                report = ConnectorReport(context, steps_results, name=report_name)
                context.report = report
                return report

            # Files modified by AddChangelogEntry are relative to airbyte repo root
            for modified_file in add_changelog_entry.modified_files:
                await add_changelog_entry_result.output.file(str(modified_file)).export(str(modified_file))
                context.logger.info(f"Exported {modified_file} following the changelog entry addition.")

            report = ConnectorReport(context, steps_results, name=report_name)
            context.report = report
    return report
