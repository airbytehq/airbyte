#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import datetime
from typing import TYPE_CHECKING, List, Set

import semver
from dagger import Container, Directory
from semver import Version

from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.airbyte_ci.connectors.reports import ConnectorReport, Report
from pipelines.airbyte_ci.metadata.pipeline import MetadataValidation
from pipelines.helpers import git
from pipelines.helpers.changelog import Changelog, ChangelogEntry
from pipelines.helpers.connectors import metadata_change_helpers
from pipelines.models.steps import Step, StepResult, StepStatus

import tomli

if TYPE_CHECKING:
    from anyio import Semaphore


class AddChangelogEntries(Step):
    context: ConnectorContext
    title = "Add changelog entry"

    def __init__(
        self,
        context: ConnectorContext,
        repo_dir: Container,
        entries: Set[ChangelogEntry],
        export_docs: bool = False,
    ) -> None:
        super().__init__(context)
        self.repo_dir = repo_dir
        self.entries = entries
        self.export_docs = export_docs

    async def _run(self) -> StepResult:
        doc_path = self.context.connector.documentation_file_path
        if not doc_path.exists():
            return StepResult(
                step=self,
                status=StepStatus.SKIPPED,
                stdout="Connector does not have a documentation file.",
                output=self.repo_dir,
            )
        try:
            original_markdown = doc_path.read_text()
            changelog = Changelog(original_markdown)
            for entry in self.entries:
                changelog.add_entry(entry)
            updated_doc = changelog.to_markdown()
        except Exception as e:
            return StepResult(
                step=self, status=StepStatus.FAILURE, stderr=f"Could not add changelog entry: {e}", output=self.repo_dir, exc_info=e
            )
        updated_repo_dir = self.repo_dir.with_new_file(str(doc_path), contents=updated_doc)
        if self.export_docs:
            await updated_repo_dir.file(str(doc_path)).export(str(doc_path))
        return StepResult(
            step=self,
            status=StepStatus.SUCCESS,
            stdout=f"Added changelog entry to {doc_path}",
            output=updated_repo_dir,
        )


class BumpDockerImageTagInMetadata(Step):
    context: ConnectorContext
    title = "Upgrade the dockerImageTag to the latest version in metadata.yaml"

    def __init__(
        self,
        context: ConnectorContext,
        repo_dir: Directory,
        new_version: Version,
        export_metadata: bool = False,
    ) -> None:
        super().__init__(context)
        self.repo_dir = repo_dir
        self.new_version = new_version
        self.export_metadata = export_metadata

    @staticmethod
    def get_metadata_with_bumped_version(previous_version: str, new_version: Version, metadata_str: str) -> str:
        return metadata_str.replace("dockerImageTag: " + previous_version, "dockerImageTag: " + str(new_version))

    async def _run(self) -> StepResult:
        metadata_path = self.context.connector.metadata_file_path
        current_metadata = await metadata_change_helpers.get_current_metadata(self.repo_dir, metadata_path)
        current_metadata_str = await metadata_change_helpers.get_current_metadata_str(self.repo_dir, metadata_path)
        current_version = metadata_change_helpers.get_current_version(current_metadata)
        if current_version is None:
            return StepResult(
                step=self,
                status=StepStatus.SKIPPED,
                stdout="Can't retrieve the connector current version.",
                output=self.repo_dir,
            )
        updated_metadata_str = self.get_metadata_with_bumped_version(current_version, self.new_version, current_metadata_str)
        repo_dir_with_updated_metadata = metadata_change_helpers.get_repo_dir_with_updated_metadata_str(
            self.repo_dir, metadata_path, updated_metadata_str
        )
        metadata_validation_results = await MetadataValidation(self.context).run()
        # Exit early if the metadata file is invalid.
        if metadata_validation_results.status is not StepStatus.SUCCESS:
            return metadata_validation_results

        if self.export_metadata:
            await repo_dir_with_updated_metadata.file(str(metadata_path)).export(str(metadata_path))
        return StepResult(
            step=self,
            status=StepStatus.SUCCESS,
            stdout=f"Updated dockerImageTag from {current_version} to {self.new_version} in {metadata_path}",
            output=repo_dir_with_updated_metadata,
        )


async def run_connector_version_bump_pipeline(
    context: ConnectorContext,
    semaphore: "Semaphore",
    bump_type: str,
    changelog_entry: str,
    pull_request_number: str,
    from_changelog_entry_files: bool,
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
            changelog_entries: Set[ChangelogEntry]
            new_version: Version
            if from_changelog_entry_files:
                new_version = Changelog.get_bumped_version(context.connector.version, bump_type)
                changelog_entries = {ChangelogEntry(version=new_version, pr_number=int(pull_request_number), comment=changelog_entry, date=datetime.date.today())}
            else:
                changelog_entries, new_version = Changelog.entries_from_files(context.connector.version, {tomli .load(open(f, 'rb')) for f in context.connector.changelog_entry_files})
            update_docker_image_tag_in_metadata = BumpDockerImageTagInMetadata(
                context,
                og_repo_dir,
                new_version,
            )
            update_docker_image_tag_in_metadata_result = await update_docker_image_tag_in_metadata.run()
            repo_dir_with_updated_metadata = update_docker_image_tag_in_metadata_result.output
            steps_results.append(update_docker_image_tag_in_metadata_result)

            add_changelog_entry = AddChangelogEntries(
                context,
                repo_dir_with_updated_metadata,
                changelog_entries,
            )
            add_changelog_entry_result = await add_changelog_entry.run()
            steps_results.append(add_changelog_entry_result)
            final_repo_dir = add_changelog_entry_result.output
            await og_repo_dir.diff(final_repo_dir).export(str(git.get_git_repo_path()))
            report = ConnectorReport(context, steps_results, name="CONNECTOR VERSION BUMP RESULTS")
            context.report = report
    return report
