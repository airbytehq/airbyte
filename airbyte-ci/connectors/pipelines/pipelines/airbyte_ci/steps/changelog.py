#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from __future__ import annotations

import datetime

import semver
from dagger import Directory

from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.helpers.changelog import Changelog
from pipelines.helpers.connectors.dagger_fs import dagger_read_file, dagger_write_file
from pipelines.models.steps import StepModifyingFiles, StepResult, StepStatus


class AddChangelogEntry(StepModifyingFiles):
    context: ConnectorContext

    title = "Add changelog entry"

    def __init__(
        self,
        context: ConnectorContext,
        documentation_directory: Directory,
        new_version: str,
        comment: str,
        pull_request_number: str | int | None,
    ) -> None:
        super().__init__(context, documentation_directory)
        self.new_version = semver.VersionInfo.parse(new_version)
        self.comment = comment
        self.pull_request_number = pull_request_number or "*PR_NUMBER_PLACEHOLDER*"

    async def _run(self, pull_request_number: int | str | None = None) -> StepResult:
        if pull_request_number is None:
            # this allows passing it dynamically from a result of another action (like creating a pull request)
            pull_request_number = self.pull_request_number

        try:
            original_markdown = await dagger_read_file(self.modified_directory, self.context.connector.documentation_file_name)
        except FileNotFoundError:
            return StepResult(
                step=self,
                status=StepStatus.SKIPPED,
                stderr="Connector does not have a documentation file.",
            )

        try:
            changelog = Changelog(original_markdown)
            changelog.add_entry(self.new_version, datetime.date.today(), pull_request_number, self.comment)
            updated_doc = changelog.to_markdown()
        except Exception as e:
            return StepResult(
                step=self,
                status=StepStatus.FAILURE,
                stderr=f"Could not add changelog entry: {e}",
                output=self.modified_directory,
                exc_info=e,
            )

        self.modified_directory = dagger_write_file(self.modified_directory, self.context.connector.documentation_file_name, updated_doc)
        self.modified_files.append(self.context.connector.documentation_file_name)
        return StepResult(
            step=self,
            status=StepStatus.SUCCESS,
            stdout=f"Added changelog entry to {self.context.connector.documentation_file_name}",
            output=self.modified_directory,
        )
