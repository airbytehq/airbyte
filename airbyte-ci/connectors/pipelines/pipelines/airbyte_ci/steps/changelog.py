#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

import semver
from dagger import Directory
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.helpers.changelog import Changelog
from pipelines.models.steps import Step, StepResult, StepStatus

if TYPE_CHECKING:
    from typing import List


class AddChangelogEntry(Step):
    context: ConnectorContext
    modified_files: List[str]

    title = "Add changelog entry"

    def __init__(
        self,
        context: ConnectorContext,
        new_version: str,
        comment: str,
        pull_request_number: str | int | None,
        repo_dir: Directory | None = None,
    ) -> None:
        super().__init__(context)
        self.new_version = semver.VersionInfo.parse(new_version)
        self.comment = comment
        self.pull_request_number = pull_request_number or "*PR_NUMBER_PLACEHOLDER*"
        self.modified_files = []
        self.repo_dir = repo_dir

    async def _run(self, pull_request_number: int | str | None = None) -> StepResult:
        if self.repo_dir is None:
            self.repo_dir = await self.context.get_repo_dir(include=[str(self.context.connector.local_connector_documentation_directory)])

        if pull_request_number is None:
            # this allows passing it dynamically from a result of another action (like creating a pull request)
            pull_request_number = self.pull_request_number

        doc_path = self.context.connector.documentation_file_path
        if not doc_path or not doc_path.exists():
            return StepResult(
                step=self,
                status=StepStatus.SKIPPED,
                stdout="Connector does not have a documentation file.",
                output=self.repo_dir,
            )
        try:
            original_markdown = doc_path.read_text()
            changelog = Changelog(original_markdown)
            changelog.add_entry(self.new_version, datetime.date.today(), pull_request_number, self.comment)
            updated_doc = changelog.to_markdown()
        except Exception as e:
            return StepResult(
                step=self, status=StepStatus.FAILURE, stderr=f"Could not add changelog entry: {e}", output=self.repo_dir, exc_info=e
            )
        self.repo_dir = self.repo_dir.with_new_file(str(doc_path), contents=updated_doc)
        self.modified_files.append(doc_path)
        return StepResult(
            step=self,
            status=StepStatus.SUCCESS,
            stdout=f"Added changelog entry to {doc_path}",
            output=self.repo_dir,
        )
