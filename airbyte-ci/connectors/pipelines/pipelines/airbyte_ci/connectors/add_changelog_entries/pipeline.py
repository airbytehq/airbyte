#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import datetime
from copy import deepcopy
from typing import TYPE_CHECKING, List, Tuple

import asyncclick as click
import semver
from dagger import Container, Directory
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.airbyte_ci.connectors.reports import ConnectorReport, Report
from pipelines.helpers import git
from pipelines.helpers.connectors import metadata_change_helpers
from pipelines.models.steps import Step, StepResult, StepStatus

if TYPE_CHECKING:
    from anyio import Semaphore


class AddChangelogEntries(Step):
    context: ConnectorContext
    title = "Add changelog entries"

    def __init__(
        self,
        context: ConnectorContext,
        repo_dir: Container,
        version: str,
        days_pr_numbers_and_changelog_entries: List[Tuple[str, str, str]],
    ) -> None:
        super().__init__(context)
        self.repo_dir = repo_dir
        self.version = version
        self.days_pr_numbers_and_changelog_entries = days_pr_numbers_and_changelog_entries

    async def _run(self) -> StepResult:
        doc_path = self.context.connector.documentation_file_path
        if not doc_path.exists():
            return StepResult(
                self,
                StepStatus.SKIPPED,
                stdout="Connector does not have a documentation file.",
                output_artifact=self.repo_dir,
            )
        try:
            updated_doc = self.add_changelog_entry(doc_path.read_text())
        except Exception as e:
            return StepResult(
                self,
                StepStatus.FAILURE,
                stdout=f"Could not add changelog entry: {e}",
                output_artifact=self.repo_dir,
            )
        updated_repo_dir = self.repo_dir.with_new_file(str(doc_path), contents=updated_doc)
        return StepResult(
            self,
            StepStatus.SUCCESS,
            stdout=f"Added changelog entry to {doc_path}",
            output_artifact=updated_repo_dir,
        )

    def find_line_index_for_new_entry(self, markdown_text: str) -> int:
        lines = markdown_text.splitlines()
        for line_index, line in enumerate(lines):
            if "version" in line.lower() and "date" in line.lower() and "pull request" in line.lower() and "subject" in line.lower():
                return line_index + 2
        raise Exception("Could not find the changelog section table in the documentation file.")

    def add_changelog_entry(self, og_doc_content: str) -> str:
        lines = og_doc_content.splitlines()
        line_index_for_new_entry = self.find_line_index_for_new_entry(og_doc_content)
        for day, pr_number, changelog_entry in self.days_pr_numbers_and_changelog_entries:
            new_entry = (
                f"| {self.version} | {day} | [{pr_number}](https://github.com/airbytehq/airbyte/pull/{pr_number}) | {changelog_entry} |"
            )
            lines.insert(line_index_for_new_entry, new_entry)
        return "\n".join(lines) + "\n"


async def run_connector_add_changelog_entries_pipeline(
    context: ConnectorContext,
    semaphore: "Semaphore",
    version: str,
    days_pr_numbers_and_changelog_entries: List[Tuple[str, str, str]],
) -> Report:
    """Run a pipeline to upgrade for a single connector.

    Args:
        context (ConnectorContext): The initialized connector context.

    Returns:
        Report: The reports holding the base image version upgrade results.
    """
    async with semaphore:
        steps_results = []
        async with context:
            og_repo_dir = await context.get_repo_dir()

            add_changelog_entry = AddChangelogEntries(
                context,
                og_repo_dir,
                version,
                days_pr_numbers_and_changelog_entries,
            )
            add_changelog_entry_result = await add_changelog_entry.run()
            steps_results.append(add_changelog_entry_result)
            final_repo_dir = add_changelog_entry_result.output_artifact
            await og_repo_dir.diff(final_repo_dir).export(str(git.get_git_repo_path()))
            report = ConnectorReport(context, steps_results, name="CONNECTOR CHANGELOG ENTRIES ADDTION RESULT")
            context.report = report
    return report
