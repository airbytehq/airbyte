#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import datetime
from typing import TYPE_CHECKING

import semver
from dagger import Container, Directory
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.airbyte_ci.connectors.reports import ConnectorReport, Report
from pipelines.airbyte_ci.metadata.pipeline import MetadataValidation
from pipelines.helpers import git
from pipelines.helpers.connectors import metadata_change_helpers
from pipelines.models.steps import Step, StepResult, StepStatus

if TYPE_CHECKING:
    from anyio import Semaphore


def get_bumped_version(version: str, bump_type: str) -> str:
    current_version = semver.VersionInfo.parse(version)
    if bump_type == "patch":
        new_version = current_version.bump_patch()
    elif bump_type == "minor":
        new_version = current_version.bump_minor()
    elif bump_type == "major":
        new_version = current_version.bump_major()
    else:
        raise ValueError(f"Unknown bump type: {bump_type}")
    return str(new_version)


class AddChangelogEntry(Step):
    context: ConnectorContext
    title = "Add changelog entry"

    def __init__(
        self,
        context: ConnectorContext,
        repo_dir: Container,
        new_version: str,
        changelog_entry: str,
        pull_request_number: str,
    ) -> None:
        super().__init__(context)
        self.repo_dir = repo_dir
        self.new_version = new_version
        self.changelog_entry = changelog_entry
        self.pull_request_number = pull_request_number

    async def _run(self) -> StepResult:
        doc_path = self.context.connector.documentation_file_path
        if not doc_path.exists():
            return StepResult(
                step=self,
                status=StepStatus.SKIPPED,
                stdout="Connector does not have a documentation file.",
                output_artifact=self.repo_dir,
            )
        try:
            updated_doc = self.add_changelog_entry(doc_path.read_text())
        except Exception as e:
            return StepResult(
                step=self,
                status=StepStatus.FAILURE,
                stdout=f"Could not add changelog entry: {e}",
                output_artifact=self.repo_dir,
            )
        updated_repo_dir = self.repo_dir.with_new_file(str(doc_path), contents=updated_doc)
        return StepResult(
            step=self,
            status=StepStatus.SUCCESS,
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
        today = datetime.date.today().strftime("%Y-%m-%d")
        lines = og_doc_content.splitlines()
        line_index_for_new_entry = self.find_line_index_for_new_entry(og_doc_content)
        new_entry = f"| {self.new_version} | {today} | [{self.pull_request_number}](https://github.com/airbytehq/airbyte/pull/{self.pull_request_number}) | {self.changelog_entry} |"
        lines.insert(line_index_for_new_entry, new_entry)
        return "\n".join(lines) + "\n"


class BumpDockerImageTagInMetadata(Step):
    context: ConnectorContext
    title = "Upgrade the dockerImageTag to the latest version in metadata.yaml"

    def __init__(
        self,
        context: ConnectorContext,
        repo_dir: Directory,
        new_version: str,
    ) -> None:
        super().__init__(context)
        self.repo_dir = repo_dir
        self.new_version = new_version

    @staticmethod
    def get_metadata_with_bumped_version(previous_version: str, new_version: str, metadata_str: str) -> str:
        return metadata_str.replace("dockerImageTag: " + previous_version, "dockerImageTag: " + new_version)

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
                output_artifact=self.repo_dir,
            )
        updated_metadata_str = self.get_metadata_with_bumped_version(current_version, self.new_version, current_metadata_str)
        repo_dir_with_updated_metadata = metadata_change_helpers.get_repo_dir_with_updated_metadata_str(
            self.repo_dir, metadata_path, updated_metadata_str
        )

        metadata_validation_results = await MetadataValidation(self.context).run()
        # Exit early if the metadata file is invalid.
        if metadata_validation_results.status is not StepStatus.SUCCESS:
            return metadata_validation_results

        return StepResult(
            step=self,
            status=StepStatus.SUCCESS,
            stdout=f"Updated dockerImageTag from {current_version} to {self.new_version} in {metadata_path}",
            output_artifact=repo_dir_with_updated_metadata,
        )


async def run_connector_version_bump_pipeline(
    context: ConnectorContext,
    semaphore: "Semaphore",
    bump_type: str,
    changelog_entry: str,
    pull_request_number: str,
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
            new_version = get_bumped_version(context.connector.version, bump_type)
            update_docker_image_tag_in_metadata = BumpDockerImageTagInMetadata(
                context,
                og_repo_dir,
                new_version,
            )
            update_docker_image_tag_in_metadata_result = await update_docker_image_tag_in_metadata.run()
            repo_dir_with_updated_metadata = update_docker_image_tag_in_metadata_result.output_artifact
            steps_results.append(update_docker_image_tag_in_metadata_result)

            add_changelog_entry = AddChangelogEntry(
                context,
                repo_dir_with_updated_metadata,
                new_version,
                changelog_entry,
                pull_request_number,
            )
            add_changelog_entry_result = await add_changelog_entry.run()
            steps_results.append(add_changelog_entry_result)
            final_repo_dir = add_changelog_entry_result.output_artifact
            await og_repo_dir.diff(final_repo_dir).export(str(git.get_git_repo_path()))
            report = ConnectorReport(context, steps_results, name="CONNECTOR VERSION BUMP RESULTS")
            context.report = report
    return report
